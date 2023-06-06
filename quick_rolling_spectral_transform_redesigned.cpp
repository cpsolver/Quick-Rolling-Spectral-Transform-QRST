//  quick_rolling_spectral_transform_redesigned.cpp
//
//
//
// -----------------------------------------------
//
//  COPYRIGHT & LICENSE
//
//  (c) Copyright 2023 by Richard Fobes at www.SolutionsCreative.com.
//  All rights reserved.
//
//  Conversion of this code into another programming language
//  is also covered by the above license terms.
//
//  A more permissive license is planned for when
//  the algorithm is working correctly, but those
//  details have not yet been specified in writing.
//
//
// -----------------------------------------------
//
//  VERSION
//
//  Version 0.001  2023-April-May
//
//  An earlier attempt, written in Python, was not
//  significantly successful, so this version is
//  being written from "scratch" after learning
//  from that version.
//
//
// -----------------------------------------------
//
//  USAGE
//
//  The following sample code compiles and then executes
//  this software under a typical Windows environment
//  with the g++ compiler and the mingw32 library already
//  installed.
//
//      path=C:\Program Files (x86)\mingw-w64\i686-8.1.0-posix-dwarf-rt_v6-rev0\mingw32\bin\
//
//      g++ quick_rolling_spectral_transform_redesigned.cpp -o quick_rolling_spectral_transform_redesigned
//
//      .\quick_rolling_spectral_transform_redesigned > output_quick_rolling_spectral_transform_redesigned.txt
//
//
// -----------------------------------------------
//
//  ABOUT
//
//  This software transform an audio waveform
//  into a spectral distribution similar to what
//  the Fast Fourier Transform (FFT) does but
//  uses only one cycle of data to produce each
//  instantaneous spectral distribution.
//
//
// -----------------------------------------------


// -----------------------------------------------
//  Terminology:
//
//  As usual, higher wavelength numbers refer to
//  longer wavelengths, which are lower
//  frequencies.
//
//  The "octave" number starts at 1 for the
//  shortest-wavelength (highest-frequency) octave
//  and increases to higher numbers for longer
//  wavelengths (lower frequencies).
//
//  The calculations are done for "standard" and
//  "tripled" octaves.
//
//  The standard octaves follow signals where
//  each octave uses the average of two adjacent
//  signal values to create a single signal value
//  at the doubled longer wavelength.
//
//  The "tripled" octaves follow signals that
//  are based on groups of three samples being
//  averaged to yield the first
//  (shortest-wavelength) tripled octave.
//
//  The combination of "standard" and "tripled"
//  octaves yields the following progression of
//  wavelengths:
//
//  1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, etc.
//
//  Notice that, except at the beginning of this
//  sequence, each number is twice the size of
//  the number two positions earlier.
//
//  To understand this counting sequence, consider
//  the analogy of keys on a piano.  The sequence
//  is analogous to this progression where "#"
//  indicates "sharp":
//
//  C6, F5#, C5, F4#, C4, F3#, C3, etc.
//
//  which, when reversed to match the direction of
//  keys on a piano, is the following note
//  sequence:
//
//  C3, F3#, C4, F4#, C5, F5#, C6, etc.
//
//  Each "wavelength" counter counts the number of
//  filtered signal values for one "wavelength"
//  cycle at the current octave.  This means the
//  the wavelength counter is not the actual
//  wavelength at that octave.  A wavelength in one
//  octave is half the wavelength of the filtered
//  signal at the next "lower-frequency" octave.
//
//  At each octave, the amplitude is measured
//  based on 4 data transitions.  This requires
//  5 data values to specify those 4 data
//  transitions.
//
//  The "quadrant" number is 1 for the first
//  quadrant of one measured cycle, and 2 for the
//  second quadrant of the cycle.  The remaining
//  third and fourth quadrants are simply
//  negative amplitudes of the first and second
//  quadrants.
//
//  The concept of "quadrature" is used to
//  follow the filtered waveform at one octave.
//  This means the amplitude shifts into each
//  adjacent quadrant in a cyclic/circular
//  sequence, and does so at either a
//  "clockwise" or "counterclockwise" progression.
//  A progression to increasing quadrants indicates
//  a longer wavelength, and a progression to
//  decreasing-numbered quadrants corresponds to
//  a shorter wavelength.
//
//  When the quadrature counting is high enough
//  to overlap with the measurements in the
//  next-lower interleaved octave, that other
//  octave sequence type takes over.  For example,
//  if the quadrature counting at standard octave
//  5 indicates a wavelength that is within the
//  lower limit of tripled octave 5 then the
//  tripled octave 5 amplitude takes over from
//  the standard octave 5 amplitude.


// -----------------------------------------------
//  Begin code.
// -----------------------------------------------


// -----------------------------------------------
//  Specify libraries needed.

#include <cstring>
#include <string>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <cmath>  //  for sine function


// -----------------------------------------------
//  Declare arrays.

int update_limit_for_at_octave_and_time_pattern[ 40 ][ 200 ] ;
int filtered_signal_at_octave_and_time_offset[ 40 ][ 4 ] ;
int amplitude_at_octave[ 40 ] ;
int time_offset_at_octave[ 40 ] ;
int quadrature_phase_at_octave[ 40 ] ;
int plot_character_at_column[ 100 ] ;
int cumulative_phase_shift_at_octave[ 40 ] ;
int flag_yes_or_no_ready_at_octave[ 40 ] ;
int flag_yes_or_no_started_at_octave[ 40 ] ;
int flag_forward_or_back_tie_resolution_at_octave[ 40 ] ;
int output_sine_wave_angle_12_bits_at_octave[ 40 ] ;
int output_sine_wave_amplitude_12_bits_at_octave[ 40 ] ;
int output_current_angle_at_octave[ 40 ] ;
int output_previous_angle_at_octave[ 40 ] ;
int output_current_amplitude_at_octave[ 40 ] ;
int output_previous_amplitude_at_octave[ 40 ] ;


// -----------------------------------------------
//  Declare global constants.

const int flag_no = 0 ;
const int flag_yes = 1 ;
const int flag_forward = 1 ;
const int flag_back = 2 ;
const int octave_maximum = 9 ;
const int octave_sequence_type_standard = 1 ;
const int octave_sequence_type_tripled = 2 ;
const int octave_tripled_first = octave_maximum + 1 ;
const int time_count_maximum = 90 ;
const int column_maximum = 70 ;
const int ascii_character_space = 32 ;
const int ascii_character_period = 46 ;
const int ascii_character_asterisk = 42 ;
const int ascii_character_zero = 48 ;
const int ascii_character_A = 65 ;
const float time_scale_factor = 1.0 ;
const int one_cycle_of_12_bit_angle = 2 * 2 * 2 * 2 * 2 * 2 * 2 * 2 * 2 * 2 * 2 * 2 ;
const int angle_at_top_peak = 2 * 2 * 2 * 2 * 2 * 2 * 2 * 2 * 2 * 2 ;
const int angle_at_bottom_peak = 4 * angle_at_top_peak ;


// -----------------------------------------------
//  Declare global variables.

int octave ;
int octave_sequence_type ;
int time_count ;
int time_offset ;
int time_offset_at_higher_octave ;
int time_offset_minus_one_at_higher_octave ;
int input_sample ;
int filtered_signal_tripled ;
int signal_1 ;
int signal_2 ;
int signal_3 ;
int signal_4 ;
int signal_5 ;
int time_offset_plus_1 ;
int time_offset_plus_2 ;
int time_offset_plus_3 ;
int time_offset_plus_4 ;
int time_offset_plus_5 ;
int counter_for_group_of_three ;
int flag_yes_or_no_repeat_octave_loop ;
int previous_amplitude ;
int current_amplitude ;
int previous_quadrature_phase ;
int current_generated_frequency ;
int highest_octave_updated ;
int column ;
int smooth_sine_wave_value ;
int angle_as_12_bits ;
int angle_as_12_bits_validated ;
int amplitude_as_12_bits ;


// -----------------------------------------------
//  Declare an input file for reading signal
//  sample numbers.

std::ifstream signal_sample_numbers ;


// -----------------------------------------------
//  Declare an output file for writing log info.

std::ofstream log_out ;


// -----------------------------------------------
//  Declare the spectral output file.

std::ofstream spectral_out ;



// -----------------------------------------------
// -----------------------------------------------
//  Subroutine get_next_smooth_sine_wave_value
//
//  Get the next value for a sine wave that
//  changes wavelength at the next peak, and
//  changes amplitude at the next zero crossing.
//  A person's ear is less likely to detect these
//  transitions.

void get_next_smooth_sine_wave_value( )
{


// -----------------------------------------------
//  Get the current angle, and ensure it has not
//  exceeded one cycle.

    angle_as_12_bits = output_sine_wave_angle_12_bits_at_octave[ octave ] ;
    angle_as_12_bits_validated = angle_as_12_bits % one_cycle_of_12_bit_angle ;
    if ( angle_as_12_bits != angle_as_12_bits_validated )
    {
        output_sine_wave_angle_12_bits_at_octave[ octave ] = angle_as_12_bits_validated ;
        angle_as_12_bits = angle_as_12_bits_validated ;
    }


// -----------------------------------------------
//  If the wave is at a peak, allow the wavelength
//  to change.  Otherwise continue with the
//  previous wavelength.

    if ( output_current_angle_at_octave[ octave ] != output_previous_angle_at_octave[ octave ] )
    {
        if ( ( ( angle_as_12_bits >= angle_at_top_peak ) && ( output_previous_angle_at_octave[ octave ] <= angle_at_top_peak ) ) || ( ( angle_as_12_bits >= angle_at_bottom_peak ) && ( output_previous_angle_at_octave[ octave ] <= angle_at_bottom_peak ) ) )
        {
            output_previous_angle_at_octave[ octave ] = output_current_angle_at_octave[ octave ] ;
            angle_as_12_bits = output_sine_wave_angle_12_bits_at_octave[ octave ] ;
        }
    }


// -----------------------------------------------
//  If the wave is at a zero crossing, allow the
//  amplitude to change.  Otherwise continue with
//  the previous amplitude.

    if ( output_current_angle_at_octave[ octave ] != output_previous_angle_at_octave[ octave ] )
    {
        if ( ( ( angle_as_12_bits >= angle_at_zero_crossing_downward ) && ( output_previous_angle_at_octave[ octave ] <= angle_at_zero_crossing_downward ) ) || ( ( angle_as_12_bits >= angle_at_zero_crossing_upward ) && ( output_previous_angle_at_octave[ octave ] <= angle_at_zero_crossing_upward ) ) )
        {
            output_previous_amplitude_at_octave[ octave ] = output_current_amplitude_at_octave[ octave ] ;
            amplitude_as_12_bits = output_sine_wave_amplitude_12_bits_at_octave[ octave ] ;
        }
    }


// -----------------------------------------------
//  Calculate the value.

    smooth_sine_wave_value = sin( 3.14159 * 2 * float( angle_as_12_bits / one_cycle_of_12_bit_angle ) )


// -----------------------------------------------

//  todo: write this code


// -----------------------------------------------
//  End of subroutine get_next_smooth_sine_wave_value.

}


// -----------------------------------------------
// -----------------------------------------------
//  Subroutine get_next_sample
//
//  Get the next data sample from the input
//  audio waveform.

void get_next_sample( )
{


// -----------------------------------------------
//  For now, while debugging, calculate a known
//  waveform.

        time_offset = 123 ;
        input_sample = 1 + 400 + ( 400 * get_next_smooth_sine_wave_value( ) ) ;
        current_generated_frequency -- ;


// -----------------------------------------------
//  End of subroutine get_next_sample.

}


// -----------------------------------------------
// -----------------------------------------------
//  Subroutine do_handle_next_sample
//
//  Do the calculations for the next sample.

void do_handle_next_sample( )
{


// -----------------------------------------------
//  Add the latest sample to the top-octave value
//  of the "tripled" sequence of octaves.  At the
//  end of three values, divide the sum by three.

    counter_for_group_of_three ++ ;
    if ( counter_for_group_of_three < 3 )
    {
        filtered_signal_tripled += input_sample ;
    } else
    {
        filtered_signal_tripled += input_sample ;
        filtered_signal_at_octave_and_time_offset[ octave_tripled_first ][ time_offset ] = int( filtered_signal_tripled / 3.0 ) ;
        counter_for_group_of_three = 0 ;
        filtered_signal_tripled = 0 ;
    }


// -----------------------------------------------
//  Begin a loop that first handles "standard"
//  octaves and then handles "tripled" octaves.
//
//  The standard sequence of octaves starts at
//  array_index 1.  The tripled sequence of
//  octaves starts at octave_tripled_first.

    for ( octave_sequence_type = octave_sequence_type_standard ; octave_sequence_type <= octave_sequence_type_standard ; octave_sequence_type ++ )
//    for ( octave_sequence_type = octave_sequence_type_standard ; octave_sequence_type <= octave_sequence_type_tripled ; octave_sequence_type ++ )
    {
        if ( octave_sequence_type == octave_sequence_type_standard )
        {
            octave = 0 ;
        } else
        {
            octave = octave_tripled_first - 1 ;
        }


// -----------------------------------------------
//  Begin a loop that handles each octave in the
//  standard sequence of octaves.  Usually this
//  loop will be exited early based on which
//  octave is being handled.

        highest_octave_updated = 0 ;
        flag_yes_or_no_repeat_octave_loop = flag_yes ;
        while ( flag_yes_or_no_repeat_octave_loop == flag_yes )
        {
            octave ++ ;


// -----------------------------------------------
//  If the current octave is not yet ready to be
//  calculated, exit the octave-indexed loop.
//  At each octave, readiness alternates with each
//  cycle that reaches that octave.  When an
//  octave is not ready, none of the next octaves
//  can be ready.  This pattern causes each
//  successive octave to automatically follow
//  the wavelength that is twice the length of
//  the wavelength at the prior octave.

            if ( ( octave != 1 ) && ( octave != octave_tripled_first ) )
            {
                if ( flag_yes_or_no_ready_at_octave[ octave ] == flag_no )
                {
                    flag_yes_or_no_ready_at_octave[ octave ] = flag_yes ;
                    flag_yes_or_no_repeat_octave_loop = flag_no ;
                    continue ;
                } else
                {
                    flag_yes_or_no_ready_at_octave[ octave ] = flag_no ;
                }
            }


// -----------------------------------------------
//  Silence the output amplitude until there are
//  enough signal values for one full cycle at
//  this octave.

            if ( time_offset_at_octave[ octave ] == 4 )
            {
                flag_yes_or_no_started_at_octave[ octave ] = flag_yes ;
            }


// -----------------------------------------------
//  Update the time offset for the current octave.
//  Specifically, determine which of 5 positions
//  is the next available position for the newest
//  signal value at this octave.

            time_offset_at_octave[ octave ] ++ ;
            time_offset = time_offset_at_octave[ octave ] ;
            if ( ( time_offset < 1 ) || ( time_offset > 5 ) )
            {
                time_offset_at_octave[ octave ] = 1 ;
                time_offset = 1 ;
            }


// -----------------------------------------------
//  Update the signal at the current octave.  It
//  is the average of the two most recent signal
//  values at the previous (higher-frequency)
//  octave.  However, the signal at octave 1 is
//  obtained directly from the input signal.

            if ( ( octave != 1 ) && ( octave != octave_tripled_first ) )
            {
                time_offset_at_higher_octave = time_offset_at_octave[ octave - 1 ] ;
                if ( time_offset_at_higher_octave > 1 )
                {
                    time_offset_minus_one_at_higher_octave = time_offset_at_higher_octave - 1 ;
                } else
                {
                    time_offset_minus_one_at_higher_octave = 5 ;
                }
                filtered_signal_at_octave_and_time_offset[ octave ][ time_offset ] = int( ( filtered_signal_at_octave_and_time_offset[ octave - 1 ][ time_offset_minus_one_at_higher_octave ] + filtered_signal_at_octave_and_time_offset[ octave - 1 ][ time_offset_at_higher_octave ] ) / 2 ) ;
            } else
            {
                filtered_signal_at_octave_and_time_offset[ 1 ][ time_offset ] = input_sample ;
            }


// -----------------------------------------------
//  Get the five most recent signal values for
//  the current octave.

            switch ( time_offset )
            {
                case 1 :
                    signal_1 = filtered_signal_at_octave_and_time_offset[ octave ][ 1 ] ;
                    signal_2 = filtered_signal_at_octave_and_time_offset[ octave ][ 2 ] ;
                    signal_3 = filtered_signal_at_octave_and_time_offset[ octave ][ 3 ] ;
                    signal_4 = filtered_signal_at_octave_and_time_offset[ octave ][ 4 ] ;
                    signal_5 = filtered_signal_at_octave_and_time_offset[ octave - 1 ][ time_offset_at_higher_octave ] ;
                    break ;
                case 2 :
                    signal_1 = filtered_signal_at_octave_and_time_offset[ octave ][ 2 ] ;
                    signal_2 = filtered_signal_at_octave_and_time_offset[ octave ][ 3 ] ;
                    signal_3 = filtered_signal_at_octave_and_time_offset[ octave ][ 4 ] ;
                    signal_4 = filtered_signal_at_octave_and_time_offset[ octave ][ 5 ] ;
                    signal_5 = filtered_signal_at_octave_and_time_offset[ octave ][ 1 ] ;
                    break ;
                case 3 :
                    signal_1 = filtered_signal_at_octave_and_time_offset[ octave ][ 3 ] ;
                    signal_2 = filtered_signal_at_octave_and_time_offset[ octave ][ 4 ] ;
                    signal_3 = filtered_signal_at_octave_and_time_offset[ octave ][ 5 ] ;
                    signal_4 = filtered_signal_at_octave_and_time_offset[ octave ][ 1 ] ;
                    signal_5 = filtered_signal_at_octave_and_time_offset[ octave ][ 2 ] ;
                    break ;
                case 4 :
                    signal_1 = filtered_signal_at_octave_and_time_offset[ octave ][ 4 ] ;
                    signal_2 = filtered_signal_at_octave_and_time_offset[ octave ][ 5 ] ;
                    signal_3 = filtered_signal_at_octave_and_time_offset[ octave ][ 1 ] ;
                    signal_4 = filtered_signal_at_octave_and_time_offset[ octave ][ 2 ] ;
                    signal_5 = filtered_signal_at_octave_and_time_offset[ octave ][ 3 ] ;
                    break ;
                default :
                    signal_1 = filtered_signal_at_octave_and_time_offset[ octave ][ 5 ] ;
                    signal_2 = filtered_signal_at_octave_and_time_offset[ octave ][ 1 ] ;
                    signal_3 = filtered_signal_at_octave_and_time_offset[ octave ][ 2 ] ;
                    signal_4 = filtered_signal_at_octave_and_time_offset[ octave ][ 3 ] ;
                    signal_5 = filtered_signal_at_octave_and_time_offset[ octave ][ 4 ] ;
                    break ;
            }


// -----------------------------------------------
//  Calculate the momentary amplitude of one cycle
//  at the current wavelength.
//
//  This calculation is based on "downward"
//  contributions for the progressions from
//  signal_1 to signal_2, signal_2 to signal_3,
//  signal_1 to signal_3, and signal_1 to
//  signal_4, and "upward" progressions from
//  signal_3 to signal_4, signal_3 to signal_4,
//  signal_3 to signal_5, signal_4 to signal_5,
//  and signal_2 to signal_5.
//  The other pairwise comparisons are not
//  significant.
//
//  Later, to increase speed, omit the
//  division here and instead do
//  division later over multiple values.

            previous_amplitude = amplitude_at_octave[ octave ] ;
            if ( flag_yes_or_no_started_at_octave[ octave ] == flag_yes )
            {
                current_amplitude = int( ( ( 3 * ( signal_1 + signal_5 ) ) - ( 4 * signal_3 ) - signal_2 - signal_4 ) / 8 ) ;
            } else
            {
                current_amplitude = 0 ;
            }
            amplitude_at_octave[ octave ] = current_amplitude ;

            log_out << current_amplitude << "  " ;


// -----------------------------------------------
//  Track the quadrature phase shift at this
//  octave.  Specifically, keep track of which
//  quadrant contains the just-calculated
//  amplitude.  The change can only be to an
//  adjacent quadrant.  The "clockwise" direction
//  can be thought of as the sequence 1, 2, 3, 4
//  and the "counterclockwise" direction can be
//  thought of as 4, 3, 2, 1.

//  this section of code is still being written ...

            switch ( quadrature_phase_at_octave[ octave ] )
            {
                case 1 :
                    if ( ( current_amplitude > 0 ) && ( previous_amplitude > 0 ) )
                    {
                        quadrature_phase_at_octave[ octave ] = 2 ;
                        cumulative_phase_shift_at_octave[ octave ] ++ ;
                    } else
                    {
                        quadrature_phase_at_octave[ octave ] = 4 ;
                        cumulative_phase_shift_at_octave[ octave ] -- ;
                    }
                    break ;
                case 2 :
                    if ( ( current_amplitude < 0 ) && ( previous_amplitude > 0 ) )
                    {
                        quadrature_phase_at_octave[ octave ] = 3 ;
                        cumulative_phase_shift_at_octave[ octave ] ++ ;
                    } else
                    {
                        quadrature_phase_at_octave[ octave ] = 1 ;
                        cumulative_phase_shift_at_octave[ octave ] -- ;
                    }
                    break ;
                case 3 :
                    if ( ( current_amplitude < 0 ) && ( previous_amplitude < 0 ) )
                    {
                        quadrature_phase_at_octave[ octave ] = 4 ;
                        cumulative_phase_shift_at_octave[ octave ] ++ ;
                    } else
                    {
                        quadrature_phase_at_octave[ octave ] = 2 ;
                        cumulative_phase_shift_at_octave[ octave ] -- ;
                    }
                    break ;
                case 4 :
                    if ( ( current_amplitude > 0 ) && ( previous_amplitude < 0 ) )
                    {
                        quadrature_phase_at_octave[ octave ] = 1 ;
                        cumulative_phase_shift_at_octave[ octave ] ++ ;
                    } else
                    {
                        quadrature_phase_at_octave[ octave ] = 3 ;
                        cumulative_phase_shift_at_octave[ octave ] -- ;
                    }
                    break ;
            }


// -----------------------------------------------
//  For logging purposes, keep track of the
//  highest octave that was updated at this time.

            highest_octave_updated = octave ;


// -----------------------------------------------
//  Repeat the loop to handle the next octave.

        }


// -----------------------------------------------
//  Repeat the loop to handle the other kind of
//  sequence of octaves.

    }


// -----------------------------------------------
//  Plot the data as digits positioned within a
//  line of text.  The smaller-numbered octaves
//  (with shorter wavelengths) are written last
//  so they overwrite the longer wavelengths.

    log_out << std::endl ;
    for ( column = 1 ; column <= column_maximum ; column ++ )
    {
        plot_character_at_column[ column ] = ascii_character_space ;
    }
    plot_character_at_column[ 35 ] = ascii_character_period ;
    for ( octave = highest_octave_updated ; octave >= 1 ; octave -- )
    {
        column = 35 + int( amplitude_at_octave[ octave ] / 30.0 ) ;
        if ( column > column_maximum )
        {
            column = column_maximum ;
        }
        if ( column < 1 )
        {
            column = 1 ;
        }
        plot_character_at_column[ column ] = ascii_character_zero + octave ;
    }
    for ( column = 1 ; column <= column_maximum ; column ++ )
    {
        log_out << char( plot_character_at_column[ column ] ) ;
    }
    log_out << std::endl ;


// -----------------------------------------------
//  End of subroutine do_handle_next_sample.

}


// -----------------------------------------------
// -----------------------------------------------
//  Execution starts here.

int main( ) {



// -----------------------------------------------
//  Open the output log file.

    log_out.open ( "log_from_qrst_redesigned.txt" , std::ios::out ) ;


// -----------------------------------------------
//  Initialization.

    current_generated_frequency = 12 ;
    input_sample = 0 ;
    for ( octave = 1 ; octave <= octave_maximum ; octave ++ )
    {
        flag_yes_or_no_ready_at_octave[ octave ] = flag_no ;
        flag_yes_or_no_started_at_octave[ octave ] = flag_no ;
        for ( time_offset = 1 ; time_offset <= 5 ; time_offset ++ )
        {
            filtered_signal_at_octave_and_time_offset[ octave ][ time_offset ] = 0 ;
        }
    }


// -----------------------------------------------
//  Begin a loop that handles each data sample.

    for ( time_count = 1 ; time_count <= time_count_maximum ; time_count ++ )
    {


// -----------------------------------------------
//  Get the next data sample from the input
//  audio waveform.

        get_next_sample( ) ;


// -----------------------------------------------
//  Handle this next sample.

        do_handle_next_sample( ) ;


// -----------------------------------------------
//  Repeat the loop that handles one data sample.

    }


// -----------------------------------------------
// -----------------------------------------------
//  End of "main" code segment.

}


// -----------------------------------------------
// -----------------------------------------------
//
//  End of all code.
//
// -----------------------------------------------
// -----------------------------------------------


// -----------------------------------------------
//
//  AUTHOR
//
//  Richard Fobes, www.SolutionsCreative.com
//
//
// -----------------------------------------------
//
//  BUGS
//
//  Please report any bugs or feature requests on GitHub,
//  at the CPSolver account, in the appropriate project
//  area.  Thank you!
//
//
// -----------------------------------------------
//
//  SUPPORT
//
//  You can find documentation for this code on GitHub,
//  in the CPSolver account.
//
//
// -----------------------------------------------
//
//  COPYRIGHT & LICENSE
//
//  (c) Copyright 2023 by Richard Fobes at www.SolutionsCreative.com.
//  All rights reserved.  This license will be changed in the future.
//
//
// -----------------------------------------------
//
//  End of quick_rolling_spectral_transform_redesigned.cpp
