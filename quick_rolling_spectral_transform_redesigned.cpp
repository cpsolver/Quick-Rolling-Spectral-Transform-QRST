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

int update_limit_for_standard_at_octave_and_time_pattern[ 20 ][ 200 ] ;
int update_limit_for_tripled_at_octave_and_time_pattern[ 20 ][ 200 ] ;
int filtered_signal_standard_at_octave_and_time_offset[ 20 ][ 4 ] ;
int filtered_signal_tripled_at_octave_and_time_offset[ 20 ][ 4 ] ;
int flag_yes_or_no_ready_standard_at_octave[ 20 ] ;
int flag_yes_or_no_ready_tripled_at_octave[ 20 ] ;
int amplitude_standard_at_octave[ 20 ] ;
int amplitude_tripled_at_octave[ 20 ] ;
int time_offset_standard_at_octave[ 20 ] ;
int time_offset_tripled_at_octave[ 20 ] ;
int flag_yes_or_no_started_at_standard_octave[ 20 ] ;
int flag_yes_or_no_started_at_tripled_octave[ 20 ] ;
int plot_character_at_column[ 100 ] ;


// -----------------------------------------------
//  Define yes and no constants.

const int flag_no = 0 ;
const int flag_yes = 1 ;


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
//  Each "wavelength" number counts the number of
//  signal values for one "wavelength" cycle at
//  the current octave.  The wavelength number
//  is specific to that octave, so they have to
//  be doubled to compare a wavelength in one
//  octave to a wavelength in the next
//  "lower-frequency" octave.
//
//  At each octave the amplitude is measured
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


// -----------------------------------------------
//  Declare global constants.

const int octave_maximum = 9 ;
const int time_count_maximum = 90 ;
const int column_maximum = 70 ;
const int ascii_character_space = 32 ;
const int ascii_character_asterisk = 42 ;
const int ascii_character_zero = 48 ;
const int ascii_character_A = 65 ;
const float time_scale_factor = 1.0 ;


// -----------------------------------------------
//  Declare global variables.

int octave ;
int time_count ;
int time_offset ;
int time_offset_at_higher_octave ;
int time_offset_minus_one_at_higher_octave ;
int input_sample ;
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
int current_generated_frequency ;
int column ;


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
//  Subroutine get_next_sample
//
//  Get the next data sample from the input
//  audio waveform.

void get_next_sample( )
{


// -----------------------------------------------
//  For now, while debugging, calculate a known
//  waveform.

        input_sample = 1 + 400 + ( 400 * sin( 3.14 * float( time_scale_factor * time_count * current_generated_frequency ) ) ) ;
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
//  Begin a loop that handles each octave in the
//  standard sequence of octaves.  Usually this
//  loop will be exited early based on which
//  octave is being handled.

    flag_yes_or_no_repeat_octave_loop = flag_yes ;
    octave = 0 ;
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

        if ( octave > 1 )
        {
            if ( flag_yes_or_no_ready_standard_at_octave[ octave ] == flag_no )
            {
                flag_yes_or_no_ready_standard_at_octave[ octave ] = flag_yes ;
                flag_yes_or_no_repeat_octave_loop = flag_no ;
                continue ;
            } else
            {
                flag_yes_or_no_ready_standard_at_octave[ octave ] = flag_no ;
            }
        }


// -----------------------------------------------
//  Silence the output amplitude until there are
//  enough signal values for one full cycle at
//  this octave.

        if ( time_offset_standard_at_octave[ octave ] == 4 )
        {
            flag_yes_or_no_started_at_standard_octave[ octave ] = flag_yes ;
        }


// -----------------------------------------------
//  Update the time offset for the current octave.
//  Specifically, determine which of 5 positions
//  is the next available position for the newest
//  signal value at this octave.

        time_offset_standard_at_octave[ octave ] ++ ;
        time_offset = time_offset_standard_at_octave[ octave ] ;
        if ( ( time_offset < 1 ) || ( time_offset > 5 ) )
        {
            time_offset_standard_at_octave[ octave ] = 1 ;
            time_offset = 1 ;
        }


// -----------------------------------------------
//  Update the signal at the current octave.  It
//  is the average of the two most recent signal
//  values at the previous (higher-frequency)
//  octave.  However, the signal at octave 1 is
//  obtained directly from the input signal.

        if ( octave > 1 )
        {
            time_offset_at_higher_octave = time_offset_standard_at_octave[ octave - 1 ] ;
            if ( time_offset_at_higher_octave > 1 )
            {
                time_offset_minus_one_at_higher_octave = time_offset_at_higher_octave - 1 ;
            } else
            {
                time_offset_minus_one_at_higher_octave = 5 ;
            }
            filtered_signal_standard_at_octave_and_time_offset[ octave ][ time_offset ] = int( ( filtered_signal_standard_at_octave_and_time_offset[ octave - 1 ][ time_offset_minus_one_at_higher_octave ] + filtered_signal_standard_at_octave_and_time_offset[ octave - 1 ][ time_offset_at_higher_octave ] ) / 2 ) ;
        } else
        {
            filtered_signal_standard_at_octave_and_time_offset[ 1 ][ time_offset ] = input_sample ;
        }


// -----------------------------------------------
//  Get the five most recent signal values for
//  the current octave.

        switch ( time_offset )
        {
            case 1 :
                signal_1 = filtered_signal_standard_at_octave_and_time_offset[ octave ][ 1 ] ;
                signal_2 = filtered_signal_standard_at_octave_and_time_offset[ octave ][ 2 ] ;
                signal_3 = filtered_signal_standard_at_octave_and_time_offset[ octave ][ 3 ] ;
                signal_4 = filtered_signal_standard_at_octave_and_time_offset[ octave ][ 4 ] ;
                signal_5 = filtered_signal_standard_at_octave_and_time_offset[ octave - 1 ][ time_offset_at_higher_octave ] ;
                break ;
            case 2 :
                signal_1 = filtered_signal_standard_at_octave_and_time_offset[ octave ][ 2 ] ;
                signal_2 = filtered_signal_standard_at_octave_and_time_offset[ octave ][ 3 ] ;
                signal_3 = filtered_signal_standard_at_octave_and_time_offset[ octave ][ 4 ] ;
                signal_4 = filtered_signal_standard_at_octave_and_time_offset[ octave ][ 5 ] ;
                signal_5 = filtered_signal_standard_at_octave_and_time_offset[ octave ][ 1 ] ;
                break ;
            case 3 :
                signal_1 = filtered_signal_standard_at_octave_and_time_offset[ octave ][ 3 ] ;
                signal_2 = filtered_signal_standard_at_octave_and_time_offset[ octave ][ 4 ] ;
                signal_3 = filtered_signal_standard_at_octave_and_time_offset[ octave ][ 5 ] ;
                signal_4 = filtered_signal_standard_at_octave_and_time_offset[ octave ][ 1 ] ;
                signal_5 = filtered_signal_standard_at_octave_and_time_offset[ octave ][ 2 ] ;
                break ;
            case 4 :
                signal_1 = filtered_signal_standard_at_octave_and_time_offset[ octave ][ 4 ] ;
                signal_2 = filtered_signal_standard_at_octave_and_time_offset[ octave ][ 5 ] ;
                signal_3 = filtered_signal_standard_at_octave_and_time_offset[ octave ][ 1 ] ;
                signal_4 = filtered_signal_standard_at_octave_and_time_offset[ octave ][ 2 ] ;
                signal_5 = filtered_signal_standard_at_octave_and_time_offset[ octave ][ 3 ] ;
                break ;
            default :
                signal_1 = filtered_signal_standard_at_octave_and_time_offset[ octave ][ 5 ] ;
                signal_2 = filtered_signal_standard_at_octave_and_time_offset[ octave ][ 1 ] ;
                signal_3 = filtered_signal_standard_at_octave_and_time_offset[ octave ][ 2 ] ;
                signal_4 = filtered_signal_standard_at_octave_and_time_offset[ octave ][ 3 ] ;
                signal_5 = filtered_signal_standard_at_octave_and_time_offset[ octave ][ 4 ] ;
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
//  multiplication here and instead do
//  multiplication later over multiple values.

        if ( flag_yes_or_no_started_at_standard_octave[ octave ] == flag_yes )
        {
            amplitude_standard_at_octave[ octave ] = int( ( ( 3 * ( signal_1 + signal_5 ) ) - ( 4 * signal_3 ) - signal_2 - signal_4 ) / 8 ) ;
        } else
        {
            amplitude_standard_at_octave[ octave ] = 0 ;
        }


        log_out << amplitude_standard_at_octave[ octave ] << "  " ;



// -----------------------------------------------
//  Repeat the loop to handle the next octave.

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
    for ( octave = octave_maximum ; octave >= 2 ; octave -- )
    {
        column = 35 + int( amplitude_standard_at_octave[ octave ] / 30.0 ) ;
//        column = 5 + int( column_maximum * filtered_signal_standard_at_octave_and_time_offset[ octave ][ time_offset_standard_at_octave[ octave ] ] / 1000 ) ;
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


return ;


// -----------------------------------------------
//  Add the latest sample to the top-octave value
//  of the "triple" sequence.  At the end of three
//  values, divide the sum by three.

    counter_for_group_of_three ++ ;
    if ( counter_for_group_of_three > 3 )
    {
        counter_for_group_of_three = 1 ;
    }
    filtered_signal_tripled_at_octave_and_time_offset[ 1 ][ counter_for_group_of_three ] += input_sample ;
    if ( counter_for_group_of_three > 3 )
    {
        filtered_signal_tripled_at_octave_and_time_offset[ 1 ][ time_offset ] = int( filtered_signal_tripled_at_octave_and_time_offset[ 1 ][ time_offset ] / 3.0 ) ;
    }


// -----------------------------------------------
//  Begin a loop that handles each octave in the
//  "triple" sequence of octaves.



//  ....  Copy and edit the code and comments for
//  the standard octaves.



// -----------------------------------------------
//  Repeat the loop to handle the next octave.



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
        flag_yes_or_no_ready_standard_at_octave[ octave ] = flag_no ;
        flag_yes_or_no_ready_tripled_at_octave[ octave ] = flag_no ;
        flag_yes_or_no_started_at_standard_octave[ octave ] = flag_no ;
        flag_yes_or_no_started_at_tripled_octave[ octave ] = flag_no ;
        for ( time_offset = 1 ; time_offset <= 5 ; time_offset ++ )
        {
            filtered_signal_standard_at_octave_and_time_offset[ octave ][ time_offset ] = 0 ;
            filtered_signal_tripled_at_octave_and_time_offset[ octave ][ time_offset ] = 0 ;
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
