#!/usr/bin/env python
#
#----------------------------------------------------------------------
#
#        sample_usage_of_quick_rolling_spectral_transform.py
#        ---------------------------------------------------
#
#  This sample code demonstrates how to use the function named
#  Quick Rolling Spectral Transform
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
#
#  Note:  This code is written in Python for debugging and
#  prototyping purposes, but this code is intended to be ported
#  to other languages (especially C) and -- if properly licensed --
#  hardware environments such as an IP core or Field Programmable
#  Gate Array (FPGA).  For this reason, closing braces are inserted
#  where closing braces would appear in C.  Also, Python-specific
#  conventions (except its awkward "range" function, which does not
#  count up to the specified number [unless all three parameters are
#  supplied]) are intentionally avoided.
#
#----------------------------------------------------------------------


#----------------------------------------------------------------------
#  Import the Quick Rolling Spectral Transform function.

import quick_rolling_spectral_transform


#----------------------------------------------------------------------
#  Specify a need for the "struct" library.
#  It is used to pack/unpack binary data written to files.

import struct


#----------------------------------------------------------------------
#  Specify a need for the math library.
#  It is only needed for the "sine" function.

from math import *


#----------------------------------------------------------------------
#  Specify what spectral information is needed.

time_duration = 32000

number_of_octaves_for_calculations = 8

number_of_samples_for_wavelength_measurement = 24

number_of_cycles_between_accumulated_spectral_results = 128 * 8


#----------------------------------------------------------------------
#  The highest octave is always 15, regardless of how many octaves of
#  information are being calculated and written.

highest_octave = 15

highest_octave_plus_one = highest_octave + 1


#----------------------------------------------------------------------
#  Initialization.

maximum_time_segment_count = int( time_duration / number_of_cycles_between_accumulated_spectral_results ) + 1

waveform_file_integer = [ 0 for pointer in range( 200 ) ]

total_amplitude_at_wavelength = [ 0 for count in range( number_of_samples_for_wavelength_measurement + 1 ) ]

amplitude_at_octave = [ 0 for octave in range( highest_octave_plus_one ) ]

scaled_wavelength_at_octave = [ 0 for octave in range( highest_octave_plus_one ) ]

viewed_sample_number = [ 0 for octave in range( ( highest_octave_plus_one ) * 3 ) ]

previous_amplitude_at_octave = [ 0 for octave in range( highest_octave_plus_one ) ]

previous_wavelength_at_octave = [ 0 for octave in range( highest_octave_plus_one ) ]

highest_allowed_frequency_segment = number_of_samples_for_wavelength_measurement * highest_octave

total_amplitude_at_frequency_segment_at_time_segment = [ [ 0 for time_segment in range( maximum_time_segment_count ) ] for frequency_segment in range( highest_allowed_frequency_segment + 1 ) ]

bit_representing_octave_at_octave = [ ( 2 ** ( highest_octave - octave ) ) for octave in range( highest_octave + 1 ) ]

bit_representing_octave_at_octave[ highest_octave ] = 1

lowest_used_frequency_segment = 100

highest_used_frequency_segment = 0

highest_amplitude = 0

spectral_results_output_counter = number_of_cycles_between_accumulated_spectral_results

time_segment = 0

wavelength_value_for_compression = 0

amplitude_value_for_compression = 0

time_count_at_last_info = 0

max_4_bit_value = ( 2 ** 4 ) - 1

max_7_bit_value = ( 2 ** 7 ) - 1

max_8_bit_value = ( 2 ** 8 ) - 1

max_16_bit_value = ( 2 ** 16 ) - 1

max_24_bit_value = ( 2 ** 24 ) - 1

delay_to_plot_count = 0

spaces = " " , " " , " "   , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "  , " "


#----------------------------------------------------------------------
#  Open the input file that contains audio waveform data.

input_waveform_file = open( 'output_binary_signal_for_testing_qrst.raw' , 'rb' , 0 )

# input_waveform_file = open( 'sound_recording_votefair_ranking_unsigned_16bit_noheader.raw' , 'rb' , 0 )


#----------------------------------------------------------------------
#  Create the output file that contains compressed audio data.

compressed_audio_file = open( 'output_binary_compressed_audio.qrst' , 'wb' , 0 )


#----------------------------------------------------------------------
#  Loop for each waveform sample.

for time_counter in range( time_duration ):


#----------------------------------------------------------------------
#  Read from the sound file, and unpack the integer value.
#  Exit the loop at the end of the input file.

    try:
        packed_waveform_value = input_waveform_file.read( 2 )
        waveform_sample_as_tuple = struct.unpack( "<h" , packed_waveform_value )
    except:
        break
    # }

    scale_for_amplitude = 100.0
    waveform_sample = int( waveform_sample_as_tuple[ 0 ] * scale_for_amplitude )


#----------------------------------------------------------------------
#  Execute the Quick Rolling Spectral Transform for the next sample,
#  and get the results.

    returned_tuple = quick_rolling_spectral_transform.quick_rolling_spectral_transform( waveform_sample, number_of_octaves_for_calculations , number_of_samples_for_wavelength_measurement )

#    print( returned_tuple )

    for octave in range( highest_octave - number_of_octaves_for_calculations + 1 , highest_octave_plus_one ):
        amplitude_at_octave[ octave ] = returned_tuple[ 0 ][ octave ]
        scaled_wavelength_at_octave[ octave ] = returned_tuple[ 1 ][ octave ]
    # }


#----------------------------------------------------------------------
#  TO DO:  Move this QRST sound-compression section to a separate
#  function.
#
#  TO DO:  Revise the compression format to use sequence:
#  channel number (4 bits), octave (4 bits), wavelength
#  within octave (8 bits), amplitude (8 bits), time delay and/or
#  indication of cyclic amplitude (8, 16, or 24 bits).
#  Cyclic amplitude varies from specified amplitude to negative of
#  specified amplitude and back again in sine-wave shape (which is
#  what happens when two pure sine waves are added together).
#  Within the first byte of the time delay, reserve 250 through 255
#  for future-defined time-based functions.
#
#  TO DO:  After moving this code to a separate function, fix the
#  bug that terminates the compression data at the last update
#  instead of terminating when the input sound file terminates.
#  This will involve a call to the compression function at the end
#  of (outside) the main loop.
#
#......................................................................
#  Write a compressed version of the spectral transform data.
#  This is used to test a new "QRST" audio-compression scheme.
#  If the time between updates is too long, supply a code that
#  specifies an extra delay amount.
#
#  The number of samples per second and other meta-data (including
#  checksum values) is stored elsewhere, such as in a separate
#  "file" within a zipped file that also holds this integer stream,
#  or this information is transferred inside of packets that also
#  contain checksum values.
#
#  If the new wavelength and amplitue are the same as the previous
#  values for the specified octave, do not write anything (because
#  the wavelength will continue at that amplitude).
#
#  Octave numbers in QRST compressed form start at one, not zero.
#  Channel numbers also start at one, not zero.
#
#  The "extra" channels can be used for "intermediate octaves" that
#  straddle the main octaves.  Or these intermediate octaves can be
#  numbered above the standard octave numbers, with the metadata
#  indicating where those octave numbers begin.
#  Added intermediate octaves can improve fidelity and precision.


#......................................................................
#  Begin a loop that handles each octave.

    for octave in range( highest_octave - number_of_octaves_for_calculations + 1 , highest_octave_plus_one ):
        if ( amplitude_at_octave[ octave ] != previous_amplitude_at_octave[ octave ] ) or ( scaled_wavelength_at_octave[ octave ] != previous_wavelength_at_octave[ octave ] ):
            previous_amplitude_at_octave[ octave ] = amplitude_at_octave[ octave ]
            previous_wavelength_at_octave[ octave ] = scaled_wavelength_at_octave[ octave ]


#......................................................................
#  If there is a long time delay that exceeds the normal 8-bit-specified
#  time delay, create the code for one or more long delays.

            time_since_last_info = time_counter - time_count_at_last_info
            while time_since_last_info > max_8_bit_value:

#                print( "long time delay = %d" % time_since_last_info )

                constant_indicating_time_extension = max_8_bit_value
                ( packed_value ) = struct.pack( ">B" , constant_indicating_time_extension )
                compressed_audio_file.write( packed_value )
#                print( "wrote byte = %d" % constant_indicating_time_extension )
                if time_since_last_info <= max_16_bit_value:
                    scaled_time_extension = int( time_since_last_info / ( max_8_bit_value + 1 ) )
                    ( packed_value ) = struct.pack( ">B" , scaled_time_extension )
                    compressed_audio_file.write( packed_value )

#                    print( "wrote byte = %d" % scaled_time_extension )

                    time_since_last_info = time_since_last_info - ( scaled_time_extension * ( max_8_bit_value + 1 ) )
                else:
                    scaled_time_extension = int( int( time_since_last_info / ( max_16_bit_value + 1 ) ) % ( max_16_bit_value + 1 ) )
                    ( packed_value ) = struct.pack( ">B" , max_8_bit_value )
                    compressed_audio_file.write( packed_value )

#                    print( "wrote byte = %d" % scaled_time_extension )

                    ( packed_value ) = struct.pack( ">B" , scaled_time_extension )
                    compressed_audio_file.write( packed_value )

#                    print( "wrote byte = %d" % scaled_time_extension )

                    time_since_last_info = time_since_last_info - ( scaled_time_extension * ( max_16_bit_value + 1 ) )
                # }
            # }


#......................................................................
#  Calculate the 8-bit values for the wavelength and amplitude.

            channel_number = 1
            octave_number = octave
            channel_and_octave_numbers_combined = ( channel_number * ( max_4_bit_value + 1 ) ) + octave_number

            wavelength_value_for_compression = scaled_wavelength_at_octave[ octave ]

            amplitude_value_for_compression = int( amplitude_at_octave[ octave ] / number_of_samples_for_wavelength_measurement )
            if amplitude_value_for_compression < 0 or wavelength_value_for_compression < 1:
                amplitude_value_for_compression = 1
            # }
            amplitude_value_for_compression = int( amplitude_value_for_compression * ( 2 ** ( -10 ) ) )
            if amplitude_value_for_compression > max_8_bit_value:
                amplitude_value_for_compression = max_8_bit_value
            elif amplitude_value_for_compression < - max_8_bit_value:
                amplitude_value_for_compression = - max_8_bit_value
            # }


#......................................................................
#  Write the binary QRST-compressed data to the file.

            ( packed_value ) = struct.pack( ">BBBB" , time_since_last_info , channel_and_octave_numbers_combined , wavelength_value_for_compression , amplitude_value_for_compression )
            compressed_audio_file.write( packed_value )
            time_count_at_last_info = time_counter

#            print( "[data written:  oct=%d  wav=%d  amp=%d]\n" % ( octave_number , wavelength_value_for_compression , amplitude_value_for_compression ) )


#......................................................................
#  Repeat the loop for the next octave that has a change in amplitude
#  or wavelength.

        # }
    # }


#----------------------------------------------------------------------
#  TO DO:  Move this spectrum-plotting functionality to a separate
#  function.
#
#  TO DO:  Fix calculation of frequency within octave.
#
#  Accumulate the power spectrum values.

    for octave in range( highest_octave - number_of_octaves_for_calculations + 1 , highest_octave_plus_one ):
        scaled_wavelength_within_octave = scaled_wavelength_at_octave[ octave ]
        adjusted_amplitude = amplitude_at_octave[ octave ] * bit_representing_octave_at_octave[ octave ]
        if adjusted_amplitude > 0:

            scale_to_calculate_frequency_within_octave = 1 / 128
            # TO DO:  Use correct logrithmic scale to convert from wavelength to frequency (within octave).
            frequency_within_octave = scale_to_calculate_frequency_within_octave * scaled_wavelength_within_octave

            if frequency_within_octave > 1.0:
                frequency_within_octave = 1.0
            elif frequency_within_octave < 0.0:
                frequency_within_octave = 0.0
            # }
            frequency_segment = int( 5 * ( octave + frequency_within_octave ) )

#            print( "[oct %d  ;  wavelength %f  ;  freq within oct %f  ;  frequency segment %d  ;  amplitude %d]" % ( octave , wavelength_within_octave , frequency_within_octave , frequency_segment , adjusted_amplitude ) )

            if ( frequency_segment < highest_allowed_frequency_segment ):
                total_amplitude_at_frequency_segment_at_time_segment[ frequency_segment ][ time_segment ] = total_amplitude_at_frequency_segment_at_time_segment[ frequency_segment ][ time_segment ] + adjusted_amplitude
                if total_amplitude_at_frequency_segment_at_time_segment[ frequency_segment ][ time_segment ] > highest_amplitude:
                    highest_amplitude = total_amplitude_at_frequency_segment_at_time_segment[ frequency_segment ][ time_segment ]
                # }
            # }
            if frequency_segment > highest_used_frequency_segment:
                highest_used_frequency_segment = frequency_segment
            # }
            if frequency_segment < lowest_used_frequency_segment:
                lowest_used_frequency_segment = frequency_segment
            # }
        # }
    # }


#......................................................................
#  When requested, start accumulating the spectral-transform data
#  into a new time segment.

    if spectral_results_output_counter <= 0:
        time_segment = time_segment + 1
        spectral_results_output_counter = number_of_cycles_between_accumulated_spectral_results
    # }
    spectral_results_output_counter = spectral_results_output_counter - 1


#----------------------------------------------------------------------
#  Repeat the loop for the next waveform sample.

# }


#----------------------------------------------------------------------
#  TO DO:  Move this spectrum-plotting functionality to a separate
#  function.
#
#  Write the spectral-transform calculated data into a file
#  (as tab-separated values so they can be plotted).

final_time_segment = time_segment - 1
print( "#proc getdata\n\tdata:" )
for offset_frequency_segment in range( highest_used_frequency_segment - lowest_used_frequency_segment + 1 ):
    frequency_segment = lowest_used_frequency_segment + offset_frequency_segment
    list_of_spectral_info_as_text = [ ]
    list_of_spectral_info_as_text.append( ( "%d" % frequency_segment ) )
    for time_segment in range( final_time_segment + 1 ):
        plot_offset_per_time_segment = 3
        value_to_plot = int( ( total_amplitude_at_frequency_segment_at_time_segment[ frequency_segment ][ time_segment ] * 80 / highest_amplitude ) + ( time_segment * plot_offset_per_time_segment ) )
        if value_to_plot < 0:
            value_to_plot = 0
        # }
        if value_to_plot > 100:
            value_to_plot = 100
        # }
        list_of_spectral_info_as_text.append( ( "%d" % value_to_plot ) )
    # }
    output_string = "\t".join( list_of_spectral_info_as_text )
    print( "\t%s" % output_string )
# }


#----------------------------------------------------------------------
#  All done.


#----------------------------------------------------------------------
