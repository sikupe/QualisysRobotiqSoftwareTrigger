from os.path import join

import numpy as np
import pandas as pd

from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


def evaluate_forces():
    handles = ['left', 'right']
    distances = [42, 132]
    weights = [1, 2, 5, 10]
    actual_weights = [1.1, 1.95, 5.2, 10.0]
    actual_forces = -np.array(actual_weights) * 9.81

    def linear(x, a, b):
        return a * x + b

    a_s = []
    b_s = []

    for handle in handles:
        print(f'# Forces {handle}')
        print(
            '| Weight | Weight measured | Distance | Measured Force w/o weight | Measured Force w/ weight | Calculated weight |')
        print('|-|-|-|-|-|-|')

        x_data = []
        x_data.extend(actual_forces)
        x_data.extend(actual_forces)

        y_data = []
        y_err = []
        for distance in distances:
            y_data_unflattened = []
            y_err_unflattened = []
            for weight, actual_weight in zip(weights, actual_weights):
                path = join(handle, f'{weight}kg_{distance}mm.csv')
                data = pd.read_csv(path, sep=',', skip_blank_lines=True, on_bad_lines='skip',
                                   encoding='utf-16-le')

                end_of_zeroing = data.index[data['time(s)'] < 2][-1]
                beginning_of_force = data.index[data['time(s)'] > data['time(s)'].iloc[-1] - 3][0]

                zero_values = data['Fx'].iloc[:end_of_zeroing]
                force_values = data['Fx'].iloc[beginning_of_force:]

                zero_avg = np.average(zero_values)
                force_avg = np.average(force_values)

                zero_std = np.std(zero_values)
                force_std = np.std(force_values)

                calc_weight = force_avg / -9.81

                y_data_unflattened.append(force_avg)
                y_err_unflattened.append(force_std)

                print(
                    f'| {weight}kg | {actual_weight}kg | {distance}mm | {zero_avg:.2f} ± {zero_std:.2f} N | {force_avg:.2f} ± {force_std:.2f} N | {calc_weight:.2f} kg |')
            y_data.append(y_data_unflattened)
            y_err.append(y_err_unflattened)

        y_data = np.array(y_data)

        popt, pcov = curve_fit(linear, x_data, y_data.flatten())
        a, b = popt
        a_s.append(a)
        b_s.append(b)

        fig, ax = plt.subplots()

        x_line = np.linspace(min(x_data), max(x_data), 100)
        y_line = linear(x_line, a, b)

        ax.set_title(f'Force data fit for {handle} handle')
        ax.errorbar(actual_forces, y_data[0], yerr=y_err, fmt='+', color='blue',
                    label=f'Measurements with {distances[0]}')
        ax.errorbar(actual_forces, y_data[1], yerr=y_err, fmt='x', color='green',
                    label=f'Measurements with {distances[1]}')
        ax.plot(x_line, y_line, color='red', label='Fitted curve')

        plt.plot()
        plt.savefig(f'{handle}_force.png')
        plt.close()

    print('# Force data fit')
    print(
        'Linear regression on the function `y(x) = a * x + b` with least squares on the force data of the handles.\n\n')
    print('Results:')
    print('|Handle|a|b|')
    print('|-|-|-|')
    for i in range(len(handles)):
        print(f'|{handles[i]}|{a_s[i]:.3f}|{b_s[i]:.3f}|')

    print()
    print('Plotted data of the handles including the fit:\n')
    print('| Left handle | Right handle |')
    print('|-|-|')
    print('| ![Fit on the left handle data](left_force.png) | ![Fit on the right handle data](right_force.png) |')


def evaluate_torques():
    handles = ['left', 'right']
    distances = [42, 132]
    weights = [1, 2, 5, 10]
    actual_weights = [1.1, 1.95, 5.2, 10.0]

    for handle in handles:
        print(f'# Torques {handle}')
        print(
            '| Weight | Weight measured | Distance | Expected torque | Measured Force w/ weight | Measured torque w/o weight |')
        print('|-|-|-|-|-|-|')
        for distance in distances:
            for weight, actual_weight in zip(weights, actual_weights):
                path = join(handle, f'{weight}kg_{distance}mm.csv')
                data = pd.read_csv(path, sep=',', skip_blank_lines=True, on_bad_lines='skip',
                                   encoding='utf-16-le')

                end_of_zeroing = data.index[data['time(s)'] < 2][-1]
                beginning_of_weight = data.index[data['time(s)'] > data['time(s)'].iloc[-1] - 3][0]

                zero_values = data['Ty'].iloc[:end_of_zeroing]
                torque_values = data['Ty'].iloc[beginning_of_weight:]

                zero_avg = np.average(zero_values)
                torque_avg = np.average(torque_values)

                zero_std = np.std(zero_values)
                torque_std = np.std(torque_values)

                print(
                    f'| {weight}kg | {actual_weight}kg | {distance}mm | {(actual_weight * 9.81 * distance / 1000):.4f} Nm | {torque_avg:.4f} ± {torque_std:.4f} Nm | {zero_avg:.4f} ± {zero_std:.4f} Nm |')


def main():
    evaluate_forces()
    evaluate_torques()


if __name__ == '__main__':
    main()
