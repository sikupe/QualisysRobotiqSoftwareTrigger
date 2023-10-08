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

    def linear(x, a, b, c):
        return linearxy(x[0, :], x[1, :], a, b, c)

    def linearxy(x, y, a, b, c):
        return a * x + b * y + c

    a_s = []
    b_s = []
    c_s = []

    for handle in handles:
        print(f'#### Forces {handle}')
        print(
            '| Weight | Weight measured | Distance | Measured Force w/o weight | Measured Force w/ weight | Calculated weight |')
        print('|-|-|-|-|-|-|')

        x_data = []
        x_err = []

        y_data = []
        for i in range(2):
            for f in actual_forces:
                y_data.append(0)
                y_data.append(f)

        for distance in distances:
            for weight, actual_weight in zip(weights, actual_weights):
                path = join(handle, f'{weight}kg_{distance}mm.csv')
                data = pd.read_csv(path, sep=',', skip_blank_lines=True, on_bad_lines='skip',
                                   encoding='utf-16-le')

                end_of_zeroing = data.index[data['time(s)'] < 2][-1]
                beginning_of_force = data.index[data['time(s)'] > data['time(s)'].iloc[-1] - 3][0]

                zero_values = data['Fx'].iloc[:end_of_zeroing]
                force_values = data['Fx'].iloc[beginning_of_force:]

                m_zero_values = data['Ty'].iloc[:end_of_zeroing]
                m_force_values = data['Ty'].iloc[beginning_of_force:]

                zero_avg = np.average(zero_values)
                force_avg = np.average(force_values)

                m_zero_avg = np.average(m_zero_values)
                m_force_avg = np.average(m_force_values)

                zero_std = np.std(zero_values)
                force_std = np.std(force_values)

                m_zero_std = np.std(m_zero_values)
                m_force_std = np.std(m_force_values)

                calc_weight = force_avg / -9.81

                x_data.append([zero_avg, m_zero_avg])
                x_data.append([force_avg, m_force_avg])
                x_err.append([zero_std, m_zero_std])
                x_err.append([force_std, m_force_std])

                print(
                    f'| {weight}kg | {actual_weight}kg | {distance}mm | {zero_avg:.2f} ± {zero_std:.2f} N | {force_avg:.2f} ± {force_std:.2f} N | {calc_weight:.2f} kg |')

        x_data = np.array(x_data).T
        x_err = np.array(x_err).T

        popt, pcov = curve_fit(linear, x_data, y_data)
        a, b, c = popt
        a_s.append(a)
        b_s.append(b)
        c_s.append(c)

        fig, ax = plt.subplots(subplot_kw={"projection": '3d'})

        x_line = np.linspace(min(x_data[0,]), max(x_data[0,]), 100)
        y_line = np.linspace(min(x_data[1,]), max(x_data[1,]), 100)

        X, Y = np.meshgrid(x_line, y_line)

        Z = linearxy(X, Y, a, b, c)

        ax.plot_surface(X, Y, Z, label='Fitted plane')

        ax.set_title(f'Force data fit for {handle} handle')
        ax.errorbar(x_data[0, :], x_data[1, :], np.array(y_data), xerr=x_err[0, :], yerr=x_err[1, :], fmt='+',
                    color='blue',
                    label=f'Measurements with {distances[0]}mm')
        ax.set_xlabel('Measured force in N')
        ax.set_ylabel('Measured torque in Nm')
        ax.set_zlabel('Expected force in N')
        ax.legend()

        fig.show()

        fig.savefig(f'{handle}_force_new.png')
        plt.close()

    print('#### Force data fit')
    print(
        'Linear regression on the function `z(x) = a * x + b * y + c` with least squares on the force data of the handles.\n\n')
    print('Results:')
    print('|Handle|a|b|c|')
    print('|-|-|-|-|')
    for i in range(len(handles)):
        print(f'|{handles[i]}|{a_s[i]:.3f}|{b_s[i]:.3f}|{c_s[i]:.3f}|')

    print()
    print('Plotted data of the handles including the fit:\n')
    print('| Left handle | Right handle |')
    print('|-|-|')
    print('| ![Fit on the left handle data](left_force_new.png) | ![Fit on the right handle data](right_force_new.png) |')


def evaluate_torques():
    handles = ['left', 'right']
    distances = [42, 132]
    weights = [1, 2, 5, 10]
    actual_weights = [1.1, 1.95, 5.2, 10.0]
    actual_forces = -np.array(actual_weights) * 9.81

    def linear(x, a, b, c):
        return linearxy(x[0, :], x[1, :], a, b, c)

    def linearxy(x, y, a, b, c):
        return a * x + b * y + c

    a_s = []
    b_s = []
    c_s = []

    for handle in handles:
        print(f'#### Torques {handle}')
        print(
            '| Weight | Weight measured | Distance | Expected torque | Measured torque w/ weight | Measured torque w/o weight |')
        print('|-|-|-|-|-|-|')

        x_data = []
        x_err = []

        y_data = []
        for i in range(2):
            for f in actual_forces:
                y_data.append(0)
                y_data.append(f * distances[i] / 1000)

        for distance in distances:
            for weight, actual_weight in zip(weights, actual_weights):
                path = join(handle, f'{weight}kg_{distance}mm.csv')
                data = pd.read_csv(path, sep=',', skip_blank_lines=True, on_bad_lines='skip',
                                   encoding='utf-16-le')

                end_of_zeroing = data.index[data['time(s)'] < 2][-1]
                beginning_of_force = data.index[data['time(s)'] > data['time(s)'].iloc[-1] - 3][0]

                zero_values = data['Fx'].iloc[:end_of_zeroing]
                force_values = data['Fx'].iloc[beginning_of_force:]

                m_zero_values = data['Ty'].iloc[:end_of_zeroing]
                m_force_values = data['Ty'].iloc[beginning_of_force:]

                zero_avg = np.average(zero_values)
                force_avg = np.average(force_values)

                m_zero_avg = np.average(m_zero_values)
                m_force_avg = np.average(m_force_values)

                zero_std = np.std(zero_values)
                force_std = np.std(force_values)

                m_zero_std = np.std(m_zero_values)
                m_force_std = np.std(m_force_values)

                x_data.append([zero_avg, m_zero_avg])
                x_data.append([force_avg, m_force_avg])
                x_err.append([zero_std, m_zero_std])
                x_err.append([force_std, m_force_std])

                print(
                    f'| {weight}kg | {actual_weight}kg | {distance}mm | {(actual_weight * 9.81 * distance / 1000):.4f} Nm | {m_force_avg:.4f} ± {m_force_std:.4f} Nm | {m_zero_avg:.4f} ± {m_zero_std:.4f} Nm |')

        x_data = np.array(x_data).T
        x_err = np.array(x_err).T

        popt, pcov = curve_fit(linear, x_data, y_data)
        a, b, c = popt
        a_s.append(a)
        b_s.append(b)
        c_s.append(c)

        fig, ax = plt.subplots(subplot_kw={"projection": '3d'})

        x_line = np.linspace(min(x_data[0,]), max(x_data[0,]), 100)
        y_line = np.linspace(min(x_data[1,]), max(x_data[1,]), 100)

        X, Y = np.meshgrid(x_line, y_line)

        Z = linearxy(X, Y, a, b, c)

        ax.plot_surface(X, Y, Z, label='Fitted plane')

        ax.set_title(f'Torque data fit for {handle} handle')
        ax.errorbar(x_data[0, :], x_data[1, :], np.array(y_data), xerr=x_err[0, :], yerr=x_err[1, :], fmt='+',
                    color='blue',
                    label=f'Measurements with {distances[0]}mm')
        ax.set_xlabel('Measured force in N')
        ax.set_ylabel('Measured torque in Nm')
        ax.set_zlabel('Expected torque in Nm')
        ax.legend()

        fig.show()

        fig.savefig(f'{handle}_torque_new.png')
        plt.close()

    print('#### Torque data fit')
    print(
        'Linear regression on the function `z(x) = a * x + b * y + c` with least squares on the torque data of the handles.\n\n')
    print('Results:')
    print('|Handle|a|b|c|')
    print('|-|-|-|-|')
    for i in range(len(handles)):
        print(f'|{handles[i]}|{a_s[i]:.3f}|{b_s[i]:.3f}|{c_s[i]:.3f}|')

    print()
    print('Plotted data of the handles including the fit:\n')
    print('| Left handle | Right handle |')
    print('|-|-|')
    print('| ![Fit on the left handle data](left_torque_new.png) | ![Fit on the right handle data](right_torque_new.png) |')


def main():
    print('### Calibration measurements of the handles')
    print(
        'In order to see the magnitude of the error of the handle data, we measured weights attached in x direction for testing purposes. We used wights of 1kg (actually 1.1kg), 2kg (actually 1.95kg), 5kg (actually 5.2kg) and 10kg (actually 10kg). This gave us force data for the x-axis and torque data for the y-axis.')
    print('We measured in two different distances of the sensors (42mm and 132mm).')
    print()
    print(
        'Further more a linear regression was made with least squares in order to find the offset of the measured data.')
    print()
    print('The results can be found below.')
    evaluate_forces()
    evaluate_torques()


if __name__ == '__main__':
    main()
