#----------------------------------------------------------------------
#        quick_rolling_spectral_transform.py
#        -----------------------------------
#
#  Quick Rolling Spectral Transform (TM) (QRST) algorithmn
#
#  Copyright 2009, 2010, 2011 by
#  Richard Fobes at www.SolutionsCreative.com
#
#  This code is licensed under the Perl Artistic License
#  version 2.0 (see www.perlfoundation.org/artistic_license_2_0
#  or the copy included in the directory containing this code),
#  plus an added requirement that any hardware implementation
#  of this algorithm must be licensed under a separate contract,
#  and another added requirement that the following
#  credit be included in all copies of this software:
#
#  The Quick Rolling Spectral Transform (TM)
#  was created by Richard Fobes, who is the author of
#  "The Creative Problem Solver's Toolbox" and
#  "Ending The Hidden Unfairness In U.S. Elections" and
#  the designer of VoteFair ranking (see VoteFair.org) and
#  the software negotiation tool at NegotiationTool.com and
#  the Dashrep programming language (see Dashrep.org).
#
#  Item 14 in the Perl Artistic License is the
#  Disclaimer of Warranty, which is repeated here:
#  "THE PACKAGE IS PROVIDED BY THE COPYRIGHT HOLDER
#  AND CONTRIBUTORS "AS IS" AND WITHOUT ANY EXPRESS OR
#  IMPLIED WARRANTIES. THE IMPLIED WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE,
#  OR NON-INFRINGEMENT ARE DISCLAIMED TO THE EXTENT
#  PERMITTED BY YOUR LOCAL LAW. UNLESS REQUIRED BY LAW,
#  NO COPYRIGHT HOLDER OR CONTRIBUTOR WILL BE LIABLE FOR
#  ANY DIRECT, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL
#  DAMAGES ARISING IN ANY WAY OUT OF THE USE OF THE
#  PACKAGE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
#
#  The name "Quick Rolling Spectral Transform" is trademarked
#  (2010) by Richard Fobes at www.SolutionsCreative.com
#  to prevent the name from being co-opted.
#
#----------------------------------------------------------------------
#  Algorithm description:
#
#  Basically the QRST spectral-transform algorithm:
#  (1) low-pass and high-pass filters the waveform into octaves,
#  (2) measures the wavelength of each octave's (filtered)
#  waveform by counting peaks and the distance between peaks,
#  (4) measures the amplitude at each octave by simply
#  summing the significant up-and-down transitions,
#  (5) produces results at each octave twice as often as
#  at the next-lower octave.
#
#  This software is still in development and does not yet yield
#  an accurate spectral transform.  As further development
#  occurs -- on an open-source basis -- the accuracy is
#  expected to increase.
#  The areas of code that currently need the most work are marked
#  with "TO DO:" tags.
#
#  The insights behind this algorithmn arose over a period of
#  many years, with one insight arising on the morning of
#  2009-January-25.  That was the point at which this
#  code began to be written.  That algorithm didn't work
#  as well as expected, yet a related algorithm showed promise,
#  and that was pursued in July of 2009.  That approach was
#  simplified in November of 2010, further developments
#  were done in December of 2010 and January of 2011, and
#  a core part of the code was re-written a week before the
#  first presentation of the Quick Rolling Spectral Transform,
#  which took place at the Oregon Technology Business Center
#  (OTBC) in Beaverton, Oregon, USA.
#  The code was released by Richard Fobes into open-source
#  distribution in February of 2011.
#
#----------------------------------------------------------------------
#
#  Note:  This code is written in Python for debugging and
#  prototyping purposes, but this code is intended to be ported
#  to other languages (especially C) and -- if properly licensed --
#  hardware environments such as an IP core or Field Programmable
#  Gate Array (FPGA).  For this and other reasons, closing braces are
#  inserted where closing braces would appear in C.  Also,
#  Python-specific conventions (except its awkward "range" function,
#  which does not count up to the specified number [unless all three
#  parameters are supplied]) are intentionally avoided.
#
#  Note:  All calculations here are done in integers, not real numbers
#  or floating-point numbers.  If you have real numbers or floating-
#  point numbers as input and need them for output, simply convert
#  the input waveform values into intermediate "units" that fit
#  within binary-integer ranges.  (This applies to all software.)
#  The intermediate "units" may not have names, and may involve
#  offset values, but they always exist for any real-life values.
#  Why bother?  Doing millions of calculations in anything other than
#  integers wastes computer time and reduces precision.
#  (If it isn't already available, software can be written to "watch"
#  these (or any) calculations to determine which "units" to use -- and
#  to determine whether any caclulations need to be done in a different
#  order, such as delaying division until the final calculation.)
#
#----------------------------------------------------------------------


#----------------------------------------------------------------------
#  Specify how many samples -- at an octave -- occur between each
#  averaged wavelength measurement.
#  Smaller values provide better time resolution, but increase how
#  often information is provided by the QRST function.
#  This number can be changed as one of the parameters to this function.

number_of_samples_for_wavelength_measurement = 24


#----------------------------------------------------------------------
#  Specify how many octaves over which this function calculates
#  wavelengths and amplitudes.  This number must not exceed 15.
#  This number can be changed as one of the parameters to this function.
#  
#  Octave 15 is the highest octave, and that octave's results are always
#  calculated.  Additional octaves -- the number specified here and/or
#  as a parameter -- are also calculated according to this number of
#  octaves.
#  If 7 octaves (the number of octaves on a piano) are calculated, the
#  lowest octave is 15 - 7 + 1 = 9.

number_of_octaves_for_calculations = 7


#----------------------------------------------------------------------
#  TO DO:  Remove unused variables.
#
#  Initialization.

#  The following number must NOT be changed.
#  The lowest octave can be changed (by changing the
#  "number_of_octaves_for_calculations" parameter),
#  but the highest octave number must not be changed.
highest_octave = 15

#  Reminder: Python's "range" function stops one count short of the specified number.
highest_octave_plus_one = highest_octave + 1

time_counter = -1
not_first_time_in_function = 0
scaled_wavelength_count = 0
scaled_amplitude = 0
initial_sample = 0
previous_number_of_octaves_for_calculations = number_of_octaves_for_calculations
previous_number_of_samples_for_wavelength_measurement = 0
maximum_distance_for_valid_cycle = 32

output_wavelength_value_at_bottom_of_octave = 64
output_wavelength_value_at_center_of_octave = output_wavelength_value_at_bottom_of_octave * 2
output_wavelength_value_at_top_of_octave = ( output_wavelength_value_at_center_of_octave * 2 ) - 1

cycle_distance_at_center_of_octave = 3

maximum_considered_distance_to_recent_peak_or_trough = 12

#  The following number can be increased, but must not be reduced
#  to less than 8.
number_of_saved_samples_per_octave = 8 + maximum_considered_distance_to_recent_peak_or_trough
# number_of_saved_samples_per_octave = 8

most_recent_sample_pointer = number_of_saved_samples_per_octave - 1

next_most_recent_sample_pointer = most_recent_sample_pointer - 1

delayed_sample_pointer = 1

#  The following number must NOT be changed.
number_of_tracks = 2

opposite_track_from_track = [ 1, 0 ]

letter_for_track = [ "a" , "b" ]

peaks = 0
troughs = 1
word_for_peaks_or_troughs = [ "peaks" , "troughs" ]

bit_representing_octave_at_octave = [ 0 for octave in range( highest_octave_plus_one ) ]

filtered_sample_at_octave_and_track_and_time_offset = [ [ [ 0 for sample_time in range( number_of_saved_samples_per_octave ) ] for track in range( number_of_tracks ) ] for octave in range( highest_octave_plus_one ) ]

peak_or_trough_based_adjustment_at_octave_and_track_and_time_offset = [ [ [ [ 0 for sample_time in range( number_of_saved_samples_per_octave ) ] for track in range( number_of_tracks ) ] for octave in range( highest_octave_plus_one ) ] for peaks_or_troughs in ( 0 , 1 ) ]

unramped_sample_at_octave_and_track_and_time_offset = [ [ [ 0 for sample_time in range( number_of_saved_samples_per_octave ) ] for track in range( number_of_tracks ) ] for octave in range( highest_octave_plus_one ) ]

previous_amplitude_contribution_at_octave = [ 0 for octave in range( highest_octave_plus_one ) ]

single_sample_at_octave_and_time_offset = [ [ 0 for sample_time in range( number_of_saved_samples_per_octave ) ] for octave in range( highest_octave_plus_one ) ]

positive_gap_to_line_at_position = [ 0 for position in range( number_of_saved_samples_per_octave + 1 ) ]

distance_total_at_octave = [ 0 for octave in range( highest_octave_plus_one ) ]

count_of_peaks_and_troughs_at_octave = [ 0 for octave in range( highest_octave_plus_one ) ]

distance_between_peaks_at_octave = [ 0 for octave in range( highest_octave_plus_one ) ]

distance_between_troughs_at_octave = [ 0 for octave in range( highest_octave_plus_one ) ]

count_of_peaks_at_octave_separated_by_distance = [ [ 0 for distance in range( maximum_distance_for_valid_cycle + 1 ) ] for octave in range( highest_octave_plus_one ) ]

count_of_troughs_at_octave_separated_by_distance = [ [ 0 for distance in range( maximum_distance_for_valid_cycle + 1 ) ] for octave in range( highest_octave_plus_one ) ]

accumulated_amplitude_at_octave = [ 0 for octave in range( highest_octave_plus_one ) ]

accumulated_amplitude_at_octave_and_distance = [ [ 0 for distance in range( maximum_distance_for_valid_cycle + 1 ) ] for octave in range( highest_octave_plus_one ) ]

integer_number_for_unit_scale_factor = number_of_samples_for_wavelength_measurement

scaled_wavelength_count_that_begins_overlap_with_next_higher_octave = int( number_of_samples_for_wavelength_measurement * 0.875 * integer_number_for_unit_scale_factor )

scale_factor_for_overlap_with_next_higher_octave = integer_number_for_unit_scale_factor / (         scaled_wavelength_count_that_begins_overlap_with_next_higher_octave - int( number_of_samples_for_wavelength_measurement * 0.625 ) )

scaled_wavelength_count_that_begins_overlap_with_next_lower_octave = int( number_of_samples_for_wavelength_measurement * 1.25 * integer_number_for_unit_scale_factor )

scale_factor_for_overlap_with_next_lower_octave = integer_number_for_unit_scale_factor / ( int( number_of_samples_for_wavelength_measurement * 1.75 ) - scaled_wavelength_count_that_begins_overlap_with_next_lower_octave )

sample_counter_at_octave = [ number_of_samples_for_wavelength_measurement for count in range( highest_octave_plus_one ) ]

final_accumulated_amplitude_at_octave = [ 0 for octave in range( highest_octave_plus_one ) ]

wavelength_at_octave = [ 0 for octave in range( highest_octave_plus_one ) ]

accumulated_amplitude_total_at_octave = [ 0 for octave in range( highest_octave_plus_one ) ]

number_of_accumuated_samples_at_octave = [ 0 for octave in range( highest_octave_plus_one ) ]

scaled_wavelength_count_at_octave = [ 0 for octave in range( highest_octave_plus_one ) ]

distance_from_most_recent_peak_or_trough_pair_at_octave = [ [ ( maximum_considered_distance_to_recent_peak_or_trough + 1 ) for octave in range( highest_octave_plus_one ) ] for peak_or_trough in ( 0 , 1 ) ]

amplitude_at_most_recent_peak_or_trough_pair_at_octave = [ [ 0 for octave in range( highest_octave_plus_one ) ] for peak_or_trough in ( 0 , 1 ) ]

sample_at_time_offset = [ 0 for sample_time in range( 8 ) ]

value_to_display_for_debugging_at_octave = [ 0 for octave in range( highest_octave_plus_one ) ]

latest_peak_to_peak_distance_so_far = 0

maximum_sample_value = - ( 2 ** 10 )

minimum_sample_value = 2 ** 10

previous_time_here = 0

scale_for_plotting = 0.00001

scale_for_plotting_amplitude_result = 999.0

scale_for_plotting_wavelength_result = 999.0


#----------------------------------------------------------------------
#  Import the generate_plot_string function.

import generate_plot_string


#----------------------------------------------------------------------
#  Open the text-waveform output file.

text_waveform_file = open( 'output_text_waveform_debug_qrst.txt' , 'w' )
text_waveform_file.write( "%s" % "Waveform input plot with debug data:\n(Plot scale changes when needed to fit new data)\n\n" )


#----------------------------------------------------------------------
#----------------------------------------------------------------------
#  Define the function and its input values.

def quick_rolling_spectral_transform( current_sample, number_of_octaves_for_calculations , number_of_samples_for_wavelength_measurement ):

    "Implements the Quick Rolling Spectral Transform (QRST) algorithmn"


#----------------------------------------------------------------------
#  TO DO:  Remove unused variables.
#
#  Specify global variables to retain these values between function
#  calls.

    global time_counter
    global not_first_time_in_function
    global initial_sample
    global previous_number_of_octaves_for_calculations
    global previous_number_of_samples_for_wavelength_measurement
    global filtered_sample_at_octave_and_track_and_time_offset
    global unramped_sample_at_octave_and_track_and_time_offset
    global peak_or_trough_based_adjustment_at_octave_and_track_and_time_offset
    global single_sample_at_octave_and_time_offset
    global most_recent_sample_pointer
    global next_most_recent_sample_pointer
    global delayed_sample_pointer
    global number_of_tracks
    global sample_counter_at_octave
    global distance_total_at_octave
    global accumulated_amplitude_at_octave_and_distance
    global final_accumulated_amplitude_at_octave
    global wavelength_at_octave
    global accumulated_amplitude_at_octave
    global accumulated_amplitude_total_at_octave
    global number_of_accumuated_samples_at_octave
    global output_wavelength_value_at_bottom_of_octave
    global output_wavelength_value_at_center_of_octave
    global output_wavelength_value_at_top_of_octave
    global scaled_wavelength_count_at_octave
    global wavelength_that_begins_overlap_with_next_higher_octave
    global scale_factor_for_overlap_with_next_higher_octave
    global scaled_wavelength_count_that_begins_overlap_with_next_lower_octave
    global scale_factor_for_overlap_with_next_lower_octave
    global count_of_peaks_and_troughs_at_octave
    global distance_between_peaks_at_octave
    global distance_between_troughs_at_octave
    global count_of_peaks_at_octave_separated_by_distance
    global count_of_troughs_at_octave_separated_by_distance
    global maximum_considered_distance_to_recent_peak_or_trough
    global value_to_display_for_debugging_at_octave
    global previous_time_here
    global bit_representing_octave_at_octave
    global sample_at_time_offset
    global latest_peak_to_peak_distance_so_far
    global maximum_sample_value
    global minimum_sample_value
    global scale_for_plotting
    global scale_for_plotting_amplitude_result
    global scale_for_plotting_wavelength_result
    global distance_from_most_recent_peak_or_trough_pair_at_octave
    global amplitude_at_most_recent_peak_or_trough_pair_at_octave


#----------------------------------------------------------------------
#  If a parameter is invalid, return with an error.

    if number_of_samples_for_wavelength_measurement < 8:
        return ( 1 )
    # }


#----------------------------------------------------------------------
#  If the number of samples used for wavelength measurement have
#  changed, restart the time counter and other values.

    if ( number_of_octaves_for_calculations != previous_number_of_octaves_for_calculations ) or ( previous_number_of_samples_for_wavelength_measurement != number_of_samples_for_wavelength_measurement) :

        previous_number_of_octaves_for_calculations = number_of_octaves_for_calculations

        previous_number_of_samples_for_wavelength_measurement = number_of_samples_for_wavelength_measurement

        time_counter = 0

        initial_sample = current_sample

        bit_representing_octave_at_octave[ highest_octave ] = 1
        for octave in range( highest_octave - 1 ):
            bit_representing_octave_at_octave[ octave ] = 2 ** ( highest_octave - octave )
        # }

        filtered_sample_at_octave_and_track_and_time_offset = [ [ [ initial_sample for sample_time in range( number_of_saved_samples_per_octave ) ] for track in range( number_of_tracks ) ] for octave in range( highest_octave_plus_one ) ]

        peak_or_trough_based_adjustment_at_octave_and_track_and_time_offset = [ [ [ [ 0 for sample_time in range( number_of_saved_samples_per_octave ) ] for track in range( number_of_tracks ) ] for octave in range( highest_octave_plus_one ) ] for peaks_or_troughs in ( 0 , 1 ) ]

        sample_counter_at_octave = [ number_of_samples_for_wavelength_measurement for count in range( highest_octave_plus_one ) ]

        accumulated_amplitude_total_at_octave = [ 0 for octave in range( highest_octave_plus_one ) ]

        number_of_accumuated_samples_at_octave = [ 0 for octave in range( highest_octave_plus_one ) ]

    # }


#----------------------------------------------------------------------
#  Update a time counter.  Only the last few bits of this value are
#  used.  To allow almost-continuous calls to this function, it is reset
#  at appropriate transitions.

    time_counter = time_counter + 1
    if time_counter > 2 ** ( highest_octave * 4 ):
        time_counter = 0
    # }


#----------------------------------------------------------------------
#  For the very first sample, put the first sample value into all the
#  filtered sample positions for all the octaves.
#  This prevents an initial spike.
#  Also initialize the numbers that contain a single bit that represents
#  an octave.

    if not_first_time_in_function != 1:
        not_first_time_in_function = 1
        initial_sample = current_sample
        filtered_sample_at_octave_and_track_and_time_offset = [ [ [ initial_sample for sample_time in range( number_of_saved_samples_per_octave ) ] for track in range( number_of_tracks ) ] for octave in range( highest_octave_plus_one ) ]
        bit_representing_octave_at_octave[ highest_octave ] = 1
        for octave in range( highest_octave ):
            bit_representing_octave_at_octave[ octave ] = 2 ** ( highest_octave - octave )
        # }
    # }


#----------------------------------------------------------------------
#  Reset any amplitude and wavelength values that may have been
#  returned in the previous call to this function.

    for octave in range( highest_octave_plus_one ):
        final_accumulated_amplitude_at_octave[ octave ] = 0
        scaled_wavelength_count_at_octave[ octave ] = 0
    # }


#----------------------------------------------------------------------
#  For debugging, specify which octaves to view.
#  To view none of the octave-specific uncommented-out debugging info,
#  set this list to a single value of zero.
#  To change which information (for the selected octaves) to display
#  for debugging, comment-out code later in the function to hide
#  what you don't want to view, and un-comment the write statements
#  that write the information you want to view.

    octaves_to_view = ( 14 , )
#    octaves_to_view = ( 15 , 14 , 13 , 12 , 11 , 10 , 9 , )


#----------------------------------------------------------------------
#  For debugging purposes, indicate which octaves are being viewed.

    if time_counter == 1:
        for octave_to_view in octaves_to_view:
            text_waveform_file.write( "[viewing octave %d which has bit-representation of %d]\n" % ( octave_to_view , bit_representing_octave_at_octave[ octave_to_view ] ) )
        # }
    # }


#----------------------------------------------------------------------
#  For debugging purposes, calculate the maximum peak-to-peak distance
#  so far for this waveform.

    if current_sample > maximum_sample_value:
        maximum_sample_value = current_sample
    if current_sample < minimum_sample_value:
        minimum_sample_value = current_sample
    # }
    latest_peak_to_peak_distance_so_far = maximum_sample_value - minimum_sample_value
    half_of_latest_peak_to_peak_distance_so_far = int( latest_peak_to_peak_distance_so_far / 2 )


#----------------------------------------------------------------------
#  For debugging, display a text-based graphical representation
#  of the input sample.

    scale_for_plotting = 0.5 / half_of_latest_peak_to_peak_distance_so_far
    string_to_write = generate_plot_string.generate_plot_string( current_sample , "**" , scale_for_plotting )
#    text_waveform_file.write( "%s\n" % ( string_to_write ) )


#----------------------------------------------------------------------
#  Loop through each octave level, starting at the highest octave.
#  This order allows each octave to use the most-recently-changed
#  values from each higher octave.
#  Witin this function, octave zero is the lowest octave
#  (because Python and many programming languages make it
#  awkward to use one as the first digit in counting),
#  but at the user level --  especially in QRST compression --
#  octave one (not zero) is the lowest octave.
#  Reminder: Using a third parameter in the "range" function causes
#  the returned numbers to end at the specified second parameter
#  instead of one short of that number.

    for octave in range( highest_octave , highest_octave_plus_one - number_of_octaves_for_calculations , -1 ):


#----------------------------------------------------------------------
#  Begin handling each octave level that needs to be updated.
#  Each octave is handled only half as often as the next-higher octave.

        if ( octave == highest_octave ) or ( ( time_counter % bit_representing_octave_at_octave[ octave ] ) == 0 ):


#----------------------------------------------------------------------
#  Determine which of the two octave-level tracks is to be updated.
#  At the highest octave, always use the zero track.

            track = 0
            other_track = 1
            if octave < highest_octave:
                bit_at_next_higher_octave = ( time_counter / bit_representing_octave_at_octave[ octave ] ) % 2
                if bit_at_next_higher_octave == 0:
                    track = 1
                    other_track = 0
                # }
            # }


#----------------------------------------------------------------------
#  For the current octave and track, shift the older samples to make
#  room for the newest samples.
#  Also set the most recent peak-or-trough adjustment values to zero.

            for sample_pointer in range( number_of_saved_samples_per_octave - 1 ):
                filtered_sample_at_octave_and_track_and_time_offset[ octave ][ track ][ sample_pointer ] = filtered_sample_at_octave_and_track_and_time_offset[ octave ][ track ][ sample_pointer + 1 ]
                for peaks_or_troughs in ( 0 , 1 ):
                    peak_or_trough_based_adjustment_at_octave_and_track_and_time_offset[ peaks_or_troughs ][ octave ][ track ][ sample_pointer ] = peak_or_trough_based_adjustment_at_octave_and_track_and_time_offset[ peaks_or_troughs ][ octave ][ track ][ sample_pointer + 1 ]
                # }
            # }
            sample_pointer = most_recent_sample_pointer
            for peaks_or_troughs in ( 0 , 1 ):
                peak_or_trough_based_adjustment_at_octave_and_track_and_time_offset[ peaks_or_troughs ][ octave ][ track ][ sample_pointer ] = 0
            # }


#----------------------------------------------------------------------
#  Update the most recent "filtered" sample at the current octave.
#  For the highest octave, it equals the most-recent actual sample.
#  At the next-highest octave, it equals the sum (which is twice the
#  average) of two adjacent delayed values from the highest-octave's
#  zero track, plus adjustment values.  At any other octave, it equals
#  half the sum (which is twice the average) of four delayed filtered
#  samples from both tracks of the next-highest octave, plus
#  adjustment values.
#  The amplitudes might seem to be doubled at each octave, but the
#  average momentary value of a sine wave is about 0.7 times its peak
#  value, so the doubling compensates for these losses, and a final
#  adjustment of amplitude measurements is done in a later section.
#  The peak-and-trough adjustments are the ones calculated in a later
#  section of code, which are based on peaks and troughs identified
#  in the next-higher octave.  These adjustments remove higher-octave
#  waves that have been identified and measured in the higher octave.
#  Using delayed values provides time for the peak-and-trough
#  adjustment values to be calculated.
#  The scale for the adjustment values is based on viewing the
#  un-adjusted waveforms along with the scaled adjustment values,
#  and then verifying better filtering (out) of the higher-octave waves,
#  so it may need refinement after this code is working better.

            scale_for_adjustment_values = 0.5
            if octave == highest_octave:
                filtered_sample_at_octave_and_track_and_time_offset[ octave ][ 0 ][ most_recent_sample_pointer ] = current_sample
                sum_of_adjustment_values = 0
                sum_of_two_samples_at_higher_octave = current_sample
            elif octave == highest_octave - 1:
                sum_of_two_samples_at_higher_octave = filtered_sample_at_octave_and_track_and_time_offset[ octave + 1 ][ 0 ][ delayed_sample_pointer ] + filtered_sample_at_octave_and_track_and_time_offset[ octave + 1 ][ 0 ][ delayed_sample_pointer + 1 ]
                sum_of_adjustment_values = peak_or_trough_based_adjustment_at_octave_and_track_and_time_offset[ peaks ][ octave + 1 ][ 0 ][ delayed_sample_pointer ] + peak_or_trough_based_adjustment_at_octave_and_track_and_time_offset[ troughs ][ octave + 1 ][ 0 ][ delayed_sample_pointer + 1 ]
                filtered_sample_at_octave_and_track_and_time_offset[ octave ][ track ][ most_recent_sample_pointer ] = int( sum_of_two_samples_at_higher_octave + ( sum_of_adjustment_values * scale_for_adjustment_values ) )
            else:
                sum_of_four_samples_at_higher_octave = filtered_sample_at_octave_and_track_and_time_offset[ octave + 1 ][ 0 ][ delayed_sample_pointer ] + filtered_sample_at_octave_and_track_and_time_offset[ octave + 1 ][ 0 ][ delayed_sample_pointer + 1 ] + filtered_sample_at_octave_and_track_and_time_offset[ octave + 1 ][ 1 ][ delayed_sample_pointer ] + filtered_sample_at_octave_and_track_and_time_offset[ octave + 1 ][ 1 ][ delayed_sample_pointer + 1 ]

                sum_of_adjustment_values = peak_or_trough_based_adjustment_at_octave_and_track_and_time_offset[ peaks ][ octave + 1 ][ track ][ delayed_sample_pointer ] + peak_or_trough_based_adjustment_at_octave_and_track_and_time_offset[ troughs ][ octave + 1 ][ track ][ delayed_sample_pointer + 1 ] + peak_or_trough_based_adjustment_at_octave_and_track_and_time_offset[ peaks ][ octave + 1 ][ other_track ][ delayed_sample_pointer ] + peak_or_trough_based_adjustment_at_octave_and_track_and_time_offset[ troughs ][ octave + 1 ][ other_track ][ delayed_sample_pointer + 1 ]

                filtered_sample_at_octave_and_track_and_time_offset[ octave ][ track ][ most_recent_sample_pointer ] = int( ( sum_of_four_samples_at_higher_octave / 2 ) + ( sum_of_adjustment_values * scale_for_adjustment_values ) )
            # }

            if ( octave in octaves_to_view) and ( octave > 0 ) and ( octave < highest_octave ):

                if sum_of_two_samples_at_higher_octave > maximum_sample_value:
                    maximum_sample_value = sum_of_two_samples_at_higher_octave
                if sum_of_two_samples_at_higher_octave < minimum_sample_value:
                    minimum_sample_value = sum_of_two_samples_at_higher_octave
                # }

                sample_to_view = sum_of_two_samples_at_higher_octave
                string_to_write = generate_plot_string.generate_plot_string( sample_to_view , ( "[%02d%s]" % ( ( octave + 1 ) , letter_for_track[ track ] ) ) , scale_for_plotting )
                text_waveform_file.write( "%s\n" % ( string_to_write ) )

                sample_to_view = sum_of_adjustment_values * scale_for_adjustment_values
                string_to_write = generate_plot_string.generate_plot_string( sample_to_view , ( "<adj%02d%s>" % ( octave , letter_for_track[ track ] ) ) , scale_for_plotting )
                text_waveform_file.write( "%s\n" % ( string_to_write ) )

                sample_to_view = filtered_sample_at_octave_and_track_and_time_offset[ octave ][ track ][ most_recent_sample_pointer ] / 4
                string_to_write = generate_plot_string.generate_plot_string( sample_to_view , ( "%02d%s" % ( octave , letter_for_track[ track ] ) ) , scale_for_plotting )
                text_waveform_file.write( "%s\n" % ( string_to_write ) )

            # }


#----------------------------------------------------------------------
#  Begin a loop that first looks for peaks, and then looks for troughs.
#  When looking for troughs, the input values are mirrored vertically,
#  and that allows using the same code -- because the troughs become
#  peaks after mirroring.

            for peaks_or_troughs in ( 0 , 1 ):
                peak_or_trough_multiplier = 1
                if peaks_or_troughs == 1:
                    peak_or_trough_multiplier = -1
                # }


#----------------------------------------------------------------------
#  Effectively draw a straight line through two samples -- the
#  next-most recent sample and the older sample that is separated by
#  the time interval being tested -- and determine if all the samples
#  between these samples -- plus each neighboring sample just outside
#  the two end samples -- are below the straight line (by a significant
#  amount).  If so, the two samples are peaks (or troughs if the data
#  is mirrored) separated by the checked-for distance of either
#  2, 3, or 4 (sample intervals).
#  The wavelength at the center of the octave has a cycle distance of 3.
#  Either 5, 6, or 7 samples are involved in this calculation.

                match_at_distance = 0
                for peak_to_peak_distance_being_tested in ( 2, 3, 4 ):
                    if match_at_distance == 0:
                        number_of_samples_involved = peak_to_peak_distance_being_tested + 3
                        slope = ( ( filtered_sample_at_octave_and_track_and_time_offset[ octave ][ track ][ next_most_recent_sample_pointer ] * peak_or_trough_multiplier ) - ( filtered_sample_at_octave_and_track_and_time_offset[ octave ][ track ][ next_most_recent_sample_pointer - peak_to_peak_distance_being_tested ] * peak_or_trough_multiplier ) ) / peak_to_peak_distance_being_tested
                        straight_line_value_at_most_recent_time = ( filtered_sample_at_octave_and_track_and_time_offset[ octave ][ track ][ next_most_recent_sample_pointer ] * peak_or_trough_multiplier ) + slope
                        match_at_distance = peak_to_peak_distance_being_tested
                        largest_gap_to_line = 0
                        calculation_position = 0
                        for sample_pointer in range( most_recent_sample_pointer - number_of_samples_involved + 1 , most_recent_sample_pointer + 1 ):
                            if ( sample_pointer != next_most_recent_sample_pointer ) and ( sample_pointer != ( next_most_recent_sample_pointer - peak_to_peak_distance_being_tested ) ):
                                gap_to_line = ( filtered_sample_at_octave_and_track_and_time_offset[ octave ][ track ][ sample_pointer ] * peak_or_trough_multiplier ) - ( straight_line_value_at_most_recent_time - ( slope * ( most_recent_sample_pointer - sample_pointer ) ) )
                                if gap_to_line >= 0:
                                    match_at_distance = 0
                                    break
                                elif abs( gap_to_line ) > largest_gap_to_line:
                                    largest_gap_to_line = abs( gap_to_line )
                                # }
                                calculation_position = calculation_position + 1
                                positive_gap_to_line_at_position[ calculation_position ] = abs( gap_to_line )
                            # }
                        # }
                        scale_for_threshold_for_gap_to_line_distance = 0.01
                        threshold_gap_to_line_distance = int( largest_gap_to_line * scale_for_threshold_for_gap_to_line_distance )
                        for check_position in range( 1, calculation_position + 1 ):
                            if positive_gap_to_line_at_position[ check_position ] < threshold_gap_to_line_distance:
                                match_at_distance = 0
                                break
                            # }
                        # }
                    # }
                # }


#----------------------------------------------------------------------
#  TO DO:  If the adjustment values do not remove aliasing effects,
#  write this section to identify aliasing and then ignore looked-for
#  patterns that were otherwise regarded as peaks and troughs --
#  instead of the non-existant cycles that arise from aliasing effects.
#
#  Currently this section just contains a framework from a section of
#  code that functioned but did not correctly identify aliasing.
#
#  If a match was found, make sure that aliasing is not going on.
#  Aliasing occurs if the sampling rate (at this octave) is a large
#  portion of a wave's cycle that produces a longer-wavelength cycle
#  that does not really exist.
#  Specifically, look at the values in the next-higher octave.  If they
#  are going through a full cycle, or most of a cycle, while the samples
#  in the current octave are only changing by a part of a cycle,
#  indicate that aliasing is occurring, and that the looked-for pattern
#  has not been found.

                if ( match_at_distance != 0 ) and ( octave < highest_octave ):
                    for earlier_or_later_peak in ( 0 , 1 ):
                        if earlier_or_later_peak == 0:
                            sample_pointer = next_most_recent_sample_pointer - peak_to_peak_distance_being_tested + 1
                        else:
                            sample_pointer = next_most_recent_sample_pointer - 1
                            if sample_pointer <= next_most_recent_sample_pointer - peak_to_peak_distance_being_tested + 1:
                                break
                            # }
                        # }
                        if track == 0:
                            adjustment_for_earlier_in_other_track = 0
                            adjustment_for_later_in_other_track = 1
                        else:
                            adjustment_for_earlier_in_other_track = 0
                            adjustment_for_later_in_other_track = 1
                        # }


                        criteria_involving_next_up_octave = 1
                        if ( octave in octaves_to_view) and ( octave > 0 ):
                            alias_detected_string = "alias NOT detected"
                            if criteria_involving_next_up_octave <= 0:
                                alias_detected_string = "alias detected"
                            # }
#                            text_waveform_file.write( "earlier/later %d , %s in track %s , %s\n" % ( earlier_or_later_peak , word_for_peaks_or_troughs[ peaks_or_troughs ] , letter_for_track[ track ] , alias_detected_string ) )
                        # }


                        if ( octave in octaves_to_view) and ( octave > 0 ):
                            sample_to_view = filtered_sample_at_octave_and_track_and_time_offset[ octave ][ other_track ][ sample_pointer + adjustment_for_earlier_in_other_track ]
                            string_to_write = generate_plot_string.generate_plot_string( sample_to_view , ( "_%s" % ( letter_for_track[ other_track ] ) ) , scale_for_plotting )
#                            text_waveform_file.write( "%s\n" % ( string_to_write ) )
                            sample_to_view = filtered_sample_at_octave_and_track_and_time_offset[ octave ][ track ][ sample_pointer ]
                            string_to_write = generate_plot_string.generate_plot_string( sample_to_view , ( "_%s" % ( letter_for_track[ track ] ) ) , scale_for_plotting )
#                            text_waveform_file.write( "%s\n" % ( string_to_write ) )
                            sample_to_view = filtered_sample_at_octave_and_track_and_time_offset[ octave ][ other_track ][ sample_pointer + adjustment_for_later_in_other_track ]
                            string_to_write = generate_plot_string.generate_plot_string( sample_to_view , ( "_%s" % ( letter_for_track[ other_track ] ) ) , scale_for_plotting )
#                            text_waveform_file.write( "%s\n" % ( string_to_write ) )
                        # }
                    # }
                # }


#----------------------------------------------------------------------
#  TO DO:  Remove this section and put it where it can be accessed in
#  the future.  It failed to correctly identify aliasing situations,
#  but it (or some aspect of it) might be useful for a different purpose.
#
#  This code checks the samples in the other track (in the same
#  octave) to see if they go in the opposite direction (up or down)
#  from the direction of the peak or trough just identified
#  (in the current track).
#  If the directions are opposite, indicate that situation -- and, if
#  needed in the future, use that information.
#  Do not do this check for the top octave because it has only one track.
#
#  If this code is used in the future, improve it by checking for
#  orthogonality (crossing at something like a "90 degree angle"),
#  not just checking for opposite directions.

                if ( 1 == 2 ):
#                if ( match_at_distance != 0 ) and ( octave < highest_octave ):
                    for earlier_or_later_peak in ( 0 , 1 ):
                        if earlier_or_later_peak == 0:
                            sample_pointer = next_most_recent_sample_pointer - peak_to_peak_distance_being_tested + 1
                            direction_if_match = - peak_or_trough_multiplier
                        else:
                            sample_pointer = next_most_recent_sample_pointer - 1
                            if sample_pointer <= next_most_recent_sample_pointer - peak_to_peak_distance_being_tested + 1:
                                break
                            # }
                            direction_if_match = peak_or_trough_multiplier
                        # }
                        if track == 0:
                            adjustment_for_earlier_in_other_track = 0
                            adjustment_for_later_in_other_track = 1
                        else:
                            adjustment_for_earlier_in_other_track = 0
                            adjustment_for_later_in_other_track = 1
                        # }

                        if ( octave in octaves_to_view) and ( octave > 0 ):
                            sample_to_view = filtered_sample_at_octave_and_track_and_time_offset[ octave ][ other_track ][ sample_pointer + adjustment_for_earlier_in_other_track ]
                            string_to_write = generate_plot_string.generate_plot_string( sample_to_view , ( "_%s" % ( letter_for_track[ other_track ] ) ) , scale_for_plotting )
#                            text_waveform_file.write( "%s\n" % ( string_to_write ) )
                            sample_to_view = filtered_sample_at_octave_and_track_and_time_offset[ octave ][ track ][ sample_pointer ]
                            string_to_write = generate_plot_string.generate_plot_string( sample_to_view , ( "_%s" % ( letter_for_track[ track ] ) ) , scale_for_plotting )
#                            text_waveform_file.write( "%s\n" % ( string_to_write ) )
                            sample_to_view = filtered_sample_at_octave_and_track_and_time_offset[ octave ][ other_track ][ sample_pointer + adjustment_for_later_in_other_track ]
                            string_to_write = generate_plot_string.generate_plot_string( sample_to_view , ( "_%s" % ( letter_for_track[ other_track ] ) ) , scale_for_plotting )
#                            text_waveform_file.write( "%s\n" % ( string_to_write ) )
                        # }

                        direction_of_surrounding_samples_in_other_track = filtered_sample_at_octave_and_track_and_time_offset[ octave ][ other_track ][ sample_pointer + adjustment_for_later_in_other_track ] - filtered_sample_at_octave_and_track_and_time_offset[ octave ][ other_track ][ sample_pointer + adjustment_for_earlier_in_other_track ]

                        if ( octave in octaves_to_view) and ( octave > 0 ):
                            alias_detected_string = "alias NOT detected"
                            if ( direction_of_surrounding_samples_in_other_track * direction_if_match ) <= 0:
                                alias_detected_string = "alias detected"
                            # }
#                            text_waveform_file.write( "earlier/later %d , %s in track %s , %s\n" % ( earlier_or_later_peak , word_for_peaks_or_troughs[ peaks_or_troughs ] , letter_for_track[ track ] , alias_detected_string ) )
                        # }

                        if ( direction_of_surrounding_samples_in_other_track * direction_if_match ) <= 0:
                            match_at_distance = 0
                            break
                        # }
                    # }
                # }


#----------------------------------------------------------------------
#  If one of the looked-for patterns has been found, update the
#  peak-and-trough count, update the total distance between peaks (and
#  troughs), and calculate the peak-to-trough amplitude for this cycle.

                if match_at_distance != 0:
                    distance_total_at_octave[ octave ] = distance_total_at_octave[ octave ] + match_at_distance
                    count_of_peaks_and_troughs_at_octave[ octave ] = count_of_peaks_and_troughs_at_octave[ octave ] + 1
                    accumulated_amplitude_at_octave[ octave ] = accumulated_amplitude_at_octave[ octave ] + largest_gap_to_line

                    if ( octave in octaves_to_view) and ( octave > 0 ):
#                        text_waveform_file.write( "%s match at octave %d and distance %d with amplitude %f\n" % ( word_for_peaks_or_troughs[ peaks_or_troughs ] , octave , match_at_distance , abs( largest_gap_to_line / 10000 ) ) )
                        pass
                    # }

                # }


#----------------------------------------------------------------------
#  TO DO:  Debug this new section.  The adjustment values calculated
#  here may be incorrect, or may be offset in time, or have the wrong
#  sign.  The symptom of the bug is that lower octaves (after these
#  adjustment values have been applied) are not fully filtered (with
#  the above-identified cycles having been removed).
#
#  If one of the looked-for patterns has been found, calculate
#  adjustment values that will remove the influence of this cycle from
#  the next-lower-octave filtered samples.
#  If the adjustment value that was saved prior to this calculation
#  is (still) zero, the new adjustment equals half
#  the sample's distance from the straight line calculated above.
#  If the adjustment value is non-zero (from having been involved in
#  an earlier peak-to-peak or trough-to-trough detection), average
#  the newly calculated value with the earlier value.
#  (A third adjustment may not be possible, and at least is rare,
#  so it is not considered.)

                if match_at_distance != 0:
                    multiplier = peak_or_trough_multiplier * -1
                    half_of_cycle_amplitude = abs( largest_gap_to_line / 2 )
                    for sample_pointer in range( next_most_recent_sample_pointer - match_at_distance , next_most_recent_sample_pointer + 1 ):
                        if ( sample_pointer == next_most_recent_sample_pointer ) or ( sample_pointer == ( next_most_recent_sample_pointer - match_at_distance ) ):
                            multiplier = peak_or_trough_multiplier * -1
                        # }
                        if peak_or_trough_based_adjustment_at_octave_and_track_and_time_offset[ peaks_or_troughs ][ octave ][ track ][ sample_pointer ] == 0:
                            peak_or_trough_based_adjustment_at_octave_and_track_and_time_offset[ peaks_or_troughs ][ octave ][ track ][ sample_pointer ] = half_of_cycle_amplitude * multiplier
                        else:
                            peak_or_trough_based_adjustment_at_octave_and_track_and_time_offset[ peaks_or_troughs ][ octave ][ track ][ sample_pointer ] = int( ( peak_or_trough_based_adjustment_at_octave_and_track_and_time_offset[ peaks_or_troughs ][ octave ][ track ][ sample_pointer ] + ( half_of_cycle_amplitude * multiplier ) ) / 2 )
                        # }
                    # }
                # }

            if ( octave in octaves_to_view) and ( octave > 0 ):
                sample_to_view = initial_sample + peak_or_trough_based_adjustment_at_octave_and_track_and_time_offset[ peaks_or_troughs ][ octave ][ track ][ next_most_recent_sample_pointer ]
                string_to_write = generate_plot_string.generate_plot_string( sample_to_view , "a" , scale_for_plotting )
#                text_waveform_file.write( "%s\n" % ( string_to_write ) )
            # }


#----------------------------------------------------------------------
#  TO DO:  Add code here that calculates the adjustment values
#  mentioned at the end of the following description.
#
#  If a pair of peaks or troughs (at this octave's wavelength) have
#  been found, and another pair of peaks or troughs (of the same type)
#  were detected recently, effectively draw a straight line
#  between the two wave patterns (at the center), and check for
#  additional peaks or troughs -- between the patterns -- that
#  significantly cross the line, and count and measure those peaks
#  or troughs.  At the same time, calculate adjustment values for
#  the samples at which these line crossings are detected.

                if match_at_distance != 0:
                    distance_to_recent_peak_or_trough = distance_from_most_recent_peak_or_trough_pair_at_octave[ peaks_or_troughs ][ octave ]
                    if ( distance_to_recent_peak_or_trough - match_at_distance > 2 ) and ( distance_to_recent_peak_or_trough < maximum_considered_distance_to_recent_peak_or_trough ):
                        half_amplitude_at_recent_peak_or_trough = amplitude_at_most_recent_peak_or_trough_pair_at_octave[ peaks_or_troughs ][ octave ] / 2
                        center_of_most_recent_peak_or_trough = ( filtered_sample_at_octave_and_track_and_time_offset[ octave ][ track ][ next_most_recent_sample_pointer ] - half_amplitude_at_recent_peak_or_trough ) * peak_or_trough_multiplier
                        center_of_previously_identified_peak_or_trough = ( straight_line_value_at_most_recent_time - half_amplitude_at_recent_peak_or_trough ) * peak_or_trough_multiplier
                        slope = ( center_of_most_recent_peak_or_trough - center_of_previously_identified_peak_or_trough ) / distance_to_recent_peak_or_trough
                        count_of_line_crossings = 1
                        direction_needed_for_crossing = -1
                        threshold_for_crossings = 0.2 * half_amplitude_at_recent_peak_or_trough
                        for sample_pointer_offset in range( match_at_distance , distance_to_recent_peak_or_trough + 1 ):
                            sample_pointer = most_recent_sample_pointer - sample_pointer_offset
                            distance_from_line = center_of_most_recent_peak_or_trough - ( slope * sample_pointer_offset ) - ( filtered_sample_at_octave_and_track_and_time_offset[ octave ][ track ][ sample_pointer ] * peak_or_trough_multiplier )

#                            text_waveform_file.write( "at octave %d , sample pointer is %d , distance from line is %d ,  threshold_for_crossings %d , direction_needed_for_crossing %d\n" % ( octave , sample_pointer , distance_from_line , threshold_for_crossings , direction_needed_for_crossing ) )

                            if ( distance_from_line * direction_needed_for_crossing ) > threshold_for_crossings:
                                count_of_line_crossings = count_of_line_crossings + 1
                                direction_needed_for_crossing = direction_needed_for_crossing * -1
                            # }
                        # }
                        cycle_count = int( count_of_line_crossings / 2 )
                        additional_distance = distance_to_recent_peak_or_trough - match_at_distance - 1
                        distance_total_at_octave[ octave ] = distance_total_at_octave[ octave ] + additional_distance
                        count_of_peaks_and_troughs_at_octave[ octave ] = count_of_peaks_and_troughs_at_octave[ octave ] + cycle_count
#  if this code works, refine the next calculation...
                        accumulated_amplitude_at_octave[ octave ] = accumulated_amplitude_at_octave[ octave ] + ( largest_gap_to_line * cycle_count )
                        distance_from_most_recent_peak_or_trough_pair_at_octave[ peaks_or_troughs ][ octave ] = 0
                        amplitude_at_most_recent_peak_or_trough_pair_at_octave[ peaks_or_troughs ][ octave ] = 0

                        if ( octave in octaves_to_view) and ( octave > 0 ):
#                            text_waveform_file.write( "at octave %d , additional %d cycles over distance %d\n" % ( octave , cycle_count , additional_distance ) )
                            pass
                        # }

                    # }
                    amplitude_at_most_recent_peak_or_trough_pair_at_octave[ peaks_or_troughs ][ octave ] = largest_gap_to_line
                    distance_from_most_recent_peak_or_trough_pair_at_octave[ peaks_or_troughs ][ octave ] = 0
                # }
                distance_from_most_recent_peak_or_trough_pair_at_octave[ peaks_or_troughs ][ octave ] = distance_from_most_recent_peak_or_trough_pair_at_octave[ peaks_or_troughs ][ octave ] + 1


#----------------------------------------------------------------------
#  Repeat the loop that first looks for peaks, and then looks for troughs.

            # }


#----------------------------------------------------------------------
#  If this octave has not yet measured the signal for the specified
#  number of samples, skip over the next few sections (which calculate
#  the wavelength and amplitude values that are returned from this function).

            number_of_accumuated_samples_at_octave[ octave ] = number_of_accumuated_samples_at_octave[ octave ] + 1
            if number_of_accumuated_samples_at_octave[ octave ] >= number_of_samples_for_wavelength_measurement:


#----------------------------------------------------------------------
#  Calculate the wavelength as the time-based distance between (all)
#  peaks and troughs divided by the number of peaks and troughs.
#  The wavelength measurement is in integer counts, with a range
#  from 63 at the bottom of the octave to 255 at the top of the
#  octave.
#  When the actual wavelength values -- that can be compared from
#  one octave to any other octave -- are needed, the wavelength
#  counts must be doubled for each octave transition.

                if ( ( count_of_peaks_and_troughs_at_octave[ octave ] > 0 ) and ( distance_total_at_octave[ octave ] > 0 )  and ( accumulated_amplitude_at_octave[ octave ] > 0 ) ):
                    scaled_wavelength_count = int( ( output_wavelength_value_at_center_of_octave * distance_total_at_octave[ octave ] ) / ( count_of_peaks_and_troughs_at_octave[ octave ] * cycle_distance_at_center_of_octave ) )
                    if scaled_wavelength_count > output_wavelength_value_at_top_of_octave:
                        scaled_wavelength_count = output_wavelength_value_at_top_of_octave
                    elif scaled_wavelength_count < output_wavelength_value_at_bottom_of_octave:
                        scaled_wavelength_count = output_wavelength_value_at_bottom_of_octave
                    # }
                else:
                    scaled_wavelength_count = 0
                    accumulated_amplitude_at_octave[ octave ] = 0
                # }

                if ( octave in octaves_to_view) and ( octave > 0 ) and ( accumulated_amplitude_at_octave[ octave ] > 0 ):
#                    text_waveform_file.write( "time diff %d  octave %d  dist %d  cyclecount %d  wavelength %d  amplitude %f\n" % ( time_counter - previous_time_here , octave, distance_total_at_octave[ octave ] , count_of_peaks_and_troughs_at_octave[ octave ] , scaled_wavelength_count , ( ( accumulated_amplitude_at_octave[ octave ] * 100 ) / latest_peak_to_peak_distance_so_far ) ) )
                    previous_time_here = time_counter
                # }


#----------------------------------------------------------------------
#  Nomalize the amplitude by dividing the accumulated amplitude by the
#  number of peaks and troughs.
#  Scale the final wavelength value and put it into part of the
#  function's return value (which is an array).
#  This adjustment compensates for each octave using twice the sample
#  value at the next-higher octave, combined with a factor of 0.7
#  because random sampling of a pure sine wave produces an average
#  (absolute) sample value of about 0.7 times the peak value.

                if count_of_peaks_and_troughs_at_octave[ octave ] > 0:
                    final_accumulated_amplitude_at_octave[ octave ] = accumulated_amplitude_at_octave[ octave ] / count_of_peaks_and_troughs_at_octave[ octave ]
                else:
                    final_accumulated_amplitude_at_octave[ octave ] = accumulated_amplitude_at_octave[ octave ]
                # }
                if octave == highest_octave:
                    scale_value_for_output_amplitude = 1
                else:
                    scale_value_for_output_amplitude = ( 1 / 1.4 ) ** ( highest_octave - octave )
                # }
                final_accumulated_amplitude_at_octave[ octave ] = final_accumulated_amplitude_at_octave[ octave ] * scale_value_for_output_amplitude


#----------------------------------------------------------------------
#  Put the final wavelength value into part of the function's return
#  value (which is an array).

                scaled_wavelength_count_at_octave[ octave ] = scaled_wavelength_count


#----------------------------------------------------------------------
#  Reset values that accumulate the amplitude at this octave.

                accumulated_amplitude_at_octave[ octave ] = 0
                count_of_peaks_and_troughs_at_octave[ octave ] = 0
                distance_total_at_octave[ octave ] = 0


#----------------------------------------------------------------------
#  TO DO:  Debug this section, which has not yet been tested.
#  It might not be needed!
#  Currently these adjustments are calculated, but the adjustments are
#  disabled.
#
#  Do a final amplitude adjustment if this wavelength is in the
#  portion that overlaps with the next or previous octave.
#  A linear ramp is used as the crossover scale factor.
#  The overlapping portion is from 0.625 to 0.875  and from 1.25 to 1.75
#  of the octave's range.  The upper numbers are twice the value of
#  the lower numbers so that the overlapping range of each octave matches
#  the same overlapping ranges of the neighboring octaves.
#  If the amplitude becomes zero, set the wavelength to zero (because any
#  wavelength value is meaningless if the amplitude is zero).

                if scaled_wavelength_count < scaled_wavelength_count_that_begins_overlap_with_next_higher_octave:
                    possible_amplitude_reduction = int( ( scaled_wavelength_count_that_begins_overlap_with_next_higher_octave - scaled_wavelength_count ) * scale_factor_for_overlap_with_next_higher_octave / integer_number_for_unit_scale_factor )
#                    if possible_amplitude_reduction >= final_accumulated_amplitude_at_octave[ octave ]:
#                        final_accumulated_amplitude_at_octave[ octave ] = 0
#                    elif ( possible_amplitude_reduction > 0 ) and ( possible_amplitude_reduction < final_accumulated_amplitude_at_octave[ octave ] ):
#                        final_accumulated_amplitude_at_octave[ octave ] = final_accumulated_amplitude_at_octave[ octave ] - possible_amplitude_reduction
#                    # }
                # }
                if scaled_wavelength_count > scaled_wavelength_count_that_begins_overlap_with_next_lower_octave:
                    possible_amplitude_reduction = int( ( scaled_wavelength_count - scaled_wavelength_count_that_begins_overlap_with_next_lower_octave ) * scale_factor_for_overlap_with_next_lower_octave / integer_number_for_unit_scale_factor )
#                    if possible_amplitude_reduction >= final_accumulated_amplitude_at_octave[ octave ]:
#                        final_accumulated_amplitude_at_octave[ octave ] = 0
#                    elif ( possible_amplitude_reduction > 0 ) and ( possible_amplitude_reduction < final_accumulated_amplitude_at_octave[ octave ] ):
#                        final_accumulated_amplitude_at_octave[ octave ] = final_accumulated_amplitude_at_octave[ octave ] - possible_amplitude_reduction
#                    # }
                # }

                if final_accumulated_amplitude_at_octave[ octave ] < 1:
                    scaled_wavelength_count_at_octave[ octave ] = output_wavelength_value_at_center_of_octave
                    final_accumulated_amplitude_at_octave[ octave ] = 0
                # }


#----------------------------------------------------------------------
#  Reset the counter and finish skipping the sections that prepare
#  to return an octave's results.

                number_of_accumuated_samples_at_octave[ octave ] = 0
            # }


#----------------------------------------------------------------------
#  Decrement the sample counter that counts the number of
#  octave-specific samples needed to measure the wavelength at this
#  octave.
#  If it was zero during the current cycle, reset the counter.

            if sample_counter_at_octave[ octave ] <= 0:
                sample_counter_at_octave[ octave ] = number_of_samples_for_wavelength_measurement - 1
            else:
                sample_counter_at_octave[ octave ] = sample_counter_at_octave[ octave ] - 1
            # }


#----------------------------------------------------------------------
#  Finish skipping an octave level that does not need to be updated.

        # }


#----------------------------------------------------------------------
#  Repeat the loop for the next octave level.

    # }


#----------------------------------------------------------------------
#  For debugging, plot (non-zero) results at the specified octaves.

    for octave in octaves_to_view:
        if final_accumulated_amplitude_at_octave[ octave ] > 1:
#            text_waveform_file.write( "[result for octave %d:  wavelength %d  amplitude %f percent\n" % ( octave , scaled_wavelength_count_at_octave[ octave ] , ( ( final_accumulated_amplitude_at_octave[ octave ] * 100 ) / latest_peak_to_peak_distance_so_far ) ) )

            sample_to_view = final_accumulated_amplitude_at_octave[ octave ]
            while abs( sample_to_view * scale_for_plotting_amplitude_result ) > 0.95:
                scale_for_plotting_amplitude_result = 0.8 * scale_for_plotting_amplitude_result
            # }
            string_to_write = generate_plot_string.generate_plot_string( sample_to_view , ( "AMPL_%d_oct%02d" % ( final_accumulated_amplitude_at_octave[ octave ] , octave ) ) , scale_for_plotting_amplitude_result )
#            text_waveform_file.write( "%s\n" % ( string_to_write ) )

            sample_to_view = scaled_wavelength_count_at_octave[ octave ] - output_wavelength_value_at_center_of_octave
            while abs( sample_to_view * scale_for_plotting_wavelength_result ) > 0.95:
                scale_for_plotting_wavelength_result = 0.8 * scale_for_plotting_wavelength_result
            # }
            amplitude_stars = [ "+" for position in range( 20 ) ]
            string_indicating_amplitude = "".join( amplitude_stars[ 0 : int( final_accumulated_amplitude_at_octave[ octave ] * scale_for_plotting_amplitude_result * 5 ) ] )

            string_to_write = generate_plot_string.generate_plot_string( sample_to_view , ( "WAVL=%d oct%02d %s" % ( scaled_wavelength_count_at_octave[ octave ] , octave , string_indicating_amplitude ) ) , scale_for_plotting_wavelength_result )
            text_waveform_file.write( "%s\n" % ( string_to_write ) )

        # }
    # }


#----------------------------------------------------------------------
#  Return with the expected information.

    return ( tuple( [ final_accumulated_amplitude_at_octave[ octave ] for octave in range( highest_octave_plus_one ) ] ) , tuple( [ scaled_wavelength_count_at_octave[ octave ] for octave in range( highest_octave_plus_one ) ] ) )


#----------------------------------------------------------------------
#  All done.

# }


#----------------------------------------------------------------------
