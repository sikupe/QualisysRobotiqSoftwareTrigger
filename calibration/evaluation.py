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

    def linear(x, a, b):
        return a * x + b

    for handle in handles:
        print(f'# Forces {handle}')
        print(
            '| Weight | Weight measured | Distance | Measured Force w/o weight | Measured Force w/ weight | Calculated weight |')
        print('|-|-|-|-|-|-|')
        x_data = []
        x_data.extend(actual_weights)
        x_data.extend(actual_weights)

        x_data = np.array(x_data) * 9.81

        y_data = []
        for distance in distances:
            for weight, actual_weight in zip(weights, actual_weights):
                path = join(handle, f'{weight}kg_{distance}mm.csv')
                data = pd.read_csv(path, sep=',', skip_blank_lines=True, on_bad_lines='skip',
                                   encoding='utf-16-le')

                end_of_zeroing = data.index[data['time(s)'] < 2][-1]
                beginning_of_weight = data.index[data['time(s)'] > data['time(s)'].iloc[-1] - 3][0]

                zero_values = data['Fx'].iloc[:end_of_zeroing]
                weight_values = data['Fx'].iloc[beginning_of_weight:]

                zero_avg = np.average(zero_values)
                weight_avg = np.average(weight_values)

                zero_std = np.std(zero_values)
                weight_std = np.std(weight_values)

                calc_weight = weight_avg / 9.81

                y_data.append(calc_weight)

                print(
                    f'| {weight}kg | {actual_weight}kg | {distance}mm | {zero_avg:.2f} ± {zero_std:.2f} N | {weight_avg:.2f} ± {weight_std:.2f} N | {calc_weight:.2f} kg |')

        y_data = np.array(y_data)

        popt, pcov = curve_fit(linear, x_data, y_data)

        plt.plot()



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
