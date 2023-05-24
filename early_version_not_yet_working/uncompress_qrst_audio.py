#----------------------------------------------------------------------
#        uncompress_qrst_audio.py
#        ------------------------
#
#  This code uncompresses audio that has been compressed
#  using the Quick Rolling Spectral Transform (TM) (QRST)
#  compression method.
#
#  Copyright 2010, 2011 by
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
#  Gate Array (FPGA).  For this reason, the "de-indent" comments
#  are inserted where closing braces would appear in C, and
#  Python-specific conventions are intentionally avoided.
#
#----------------------------------------------------------------------


#----------------------------------------------------------------------
#  Specify a need for the math library.
#  It is only needed for the "cosine" function.

from math import *


#----------------------------------------------------------------------
#  Specify a need for the "struct" library.
#  It is used to pack/unpack binary data (from an audio file).

import struct


#----------------------------------------------------------------------
#  Specify a need for the "sys" library, used for text writing.

import sys


#----------------------------------------------------------------------
#  Constant that can be changed.

number_of_samples_for_wavelength_measurement = 32


#----------------------------------------------------------------------
#  Set the playback speed.  Higher numbers produce faster speeds,
#  numbers less than one produce slower speeds.

scaled_playback_speed = 1.0


#----------------------------------------------------------------------
#  TO DO:  Change this program to match the QRST compression format
#  changes that are described in the comments within the Quick Rolling
#  Spectral Transform function.


#----------------------------------------------------------------------
#  TO DO:  After fixing the QRST algorithm for proper termination of
#  audio file, ensure that this program correctly terminates.


#----------------------------------------------------------------------
#  TO DO:  Remove unused variables.
#
#  Initialization.

highest_octave = 15

lowest_octave_encountered = highest_octave

max_4_bit_value = ( 2 ** 4 ) - 1

max_7_bit_value = ( 2 ** 7 ) - 1

max_8_bit_value = ( 2 ** 8 ) - 1

max_12_bit_value = ( 2 ** 12 ) - 1

max_13_bit_value = ( 2 ** 13 ) - 1

max_14_bit_value = ( 2 ** 14 ) - 1

max_15_bit_value = ( 2 ** 15 ) - 1

max_16_bit_value = ( 2 ** 16 ) - 1

maximum_input_wavelength_count = max_8_bit_value

wavelength_count_at_center_of_octave = int( maximum_input_wavelength_count / 2 )

scale_for_wavelength_within_octave = 1 / ( maximum_input_wavelength_count - wavelength_count_at_center_of_octave )

bits_count_for_wavelength_at_center_of_octave = 7

wavelength_offset_for_negative_values = max_7_bit_value + 1

scale_for_reduction_to_zero = 0.5

threshold_for_change_to_zero = 50

time_counter = 0

maximum_time_duration = 100000

time_count_at_last_info = 0

loop_status_continue = 1

loop_status_done = 2

angle_increment = 0

maximum_channel_number = max_4_bit_value

maximum_amplitude = max_8_bit_value

maximum_wavelength = max_8_bit_value

# Reminder: Python's "range" function stops one count short of specified number

amplitude_at_octave = [ 0 for octave in range( highest_octave + 1 ) ]

wavelength_at_octave = [ 0 for octave in range( highest_octave + 1 ) ]

angle_increment_at_octave = [ 0 for octave in range( highest_octave + 1 ) ]

regeneration_angle_at_octave = [ 0 for octave in range( highest_octave + 1 ) ]

regeneration_amplitude_at_octave = [ 0 for octave in range( highest_octave + 1 ) ]

regeneration_wavelength_at_octave = [ 0 for octave in range( highest_octave + 1 ) ]

regeneration_previous_sample_at_octave = [ 0 for octave in range( highest_octave + 1 ) ]

regeneration_next_previous_sample_at_octave = [ 0 for octave in range( highest_octave + 1 ) ]

viewed_sample_number = [ 0 for octave in range( highest_octave + 1 ) ]

spaces = " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " " , " "


#----------------------------------------------------------------------
#  Open the compressed audio input file.

input_compressed_audio_file = open( 'output_binary_compressed_audio.qrst', 'rb' )


#----------------------------------------------------------------------
#  Create the output file that contains uncompressed audio data.

compressed_audio_file = open( 'output_binary_uncompressed_audio.raw' , 'wb' , 0 )


#----------------------------------------------------------------------
#  Begin a loop that repeats while compressed-audio data is available.

regenerated_audio_value = 0
time_counter = -1
accumulated_time_delay_count = 0
loop_status = loop_status_continue
while ( loop_status == loop_status_continue ) and ( time_counter < maximum_time_duration ):
    time_counter = time_counter + 1


#----------------------------------------------------------------------
#  Read the next byte (8-bit binary value) -- a time-extension value --
#  from the compressed file.  Exit the loop at the end of the input file.

    possible_time_extension = 0
    try:
        packed_value = input_compressed_audio_file.read( 1 )
        ( possible_time_extension , ) = struct.unpack( ">B" , packed_value )
    except:
        loop_status = loop_status_done
    # }


#----------------------------------------------------------------------
#  If the time extension is longer than the usual 8-bit value, get one
#  or two more bytes to determine the length of this extension, add it
#  to the accumulated time-delay count, and then repeat the loop
#  to get the next compressed data.
#  Allow for speeded-up or slowed-down playback, which scales the
#  incremental time delay.

    if possible_time_extension == max_8_bit_value:

#        print( "time delay long byte 1 = %d" % possible_time_extension )

        packed_value = input_compressed_audio_file.read( 1 )
        ( possible_time_extension , ) = struct.unpack( ">B" , packed_value )
        if possible_time_extension < max_8_bit_value:

#            print( "time delay long byte 2 = %d" % possible_time_extension )

            accumulated_time_delay_count = accumulated_time_delay_count + int( possible_time_extension * ( max_8_bit_value + 1 ) / scaled_playback_speed )
        else:
            packed_value = input_compressed_audio_file.read( 1 )
            ( possible_time_extension , ) = struct.unpack( ">B" , packed_value )

#            print( "time delay long byte 3 = %d" % possible_time_extension )

            accumulated_time_delay_count = accumulated_time_delay_count + int( possible_time_extension * ( max_16_bit_value + 1 ) / scaled_playback_speed )

        continue


#----------------------------------------------------------------------
#  Otherwise, this is a normal time delay, so update the time-delay
#  with this value, possibly with a speed adjustment.

    else:
        time_extension = possible_time_extension
        accumulated_time_delay_count = accumulated_time_delay_count + int( time_extension / scaled_playback_speed )

#        print( "normal time delay byte 0 = %d" % time_extension )


#----------------------------------------------------------------------
#  Get the new combination of channel number, octave number,
#  wavelength, and amplitude.

        try:
            packed_value = input_compressed_audio_file.read( 3 )
            ( channel_and_octave_numbers_combined , new_wavelength_value , new_amplitude_value ) = struct.unpack( ">BBB" , packed_value )
        except:
            loop_status = loop_status_done
            continue
        # }

        new_channel_number = int( channel_and_octave_numbers_combined / ( max_4_bit_value + 1 ) )
        new_octave_number = channel_and_octave_numbers_combined % ( max_4_bit_value + 1 )

#        print( "channel %d   octave %d   wavelength %d   amplitude %d" % ( new_channel_number , new_octave_number , new_wavelength_value , new_amplitude_value ) )


#----------------------------------------------------------------------
#  If the channel number is not one, set it to one.
#  It is the only channel supported here.

        if new_channel_number != 1:
            new_channel_number = 1
        # }


#----------------------------------------------------------------------
#  If the octave number is invalid -- including a value of zero -- then
#  ignore this spectral info (and get the next info).
#  Track the lowest octave number.

        if ( new_octave_number > highest_octave ) or ( new_octave_number < 1 ):
            continue
        # }
        if new_octave_number < lowest_octave_encountered:
            lowest_octave_encountered = new_octave_number
        # }


#----------------------------------------------------------------------
#  Offset the wavelength value so that negative values represent
#  wavelengths below the center of the octave.

        new_wavelength_value = new_wavelength_value - wavelength_count_at_center_of_octave


#----------------------------------------------------------------------
#  Optionally adjust the amplitude, possibly doing equalization
#  (based on wavelength).

        scale_amplitude_adjustment_for_equalization = 0.1
        if new_octave_number == 15:
            new_amplitude_value = new_amplitude_value * scale_amplitude_adjustment_for_equalization
        # }

#        print( "channel %d   octave %d   wavelength %d   amplitude %d" % ( new_channel_number , new_octave_number , new_wavelength_value , new_amplitude_value ) )


#----------------------------------------------------------------------
#  If the amplitude is now zero, ignore this spectral info, and repeat
#  the loop to get the next spectral info.

        if new_amplitude_value <= 0:
            continue
        # }


#----------------------------------------------------------------------
#  Terminate the branch that handles the choice between a long time
#  delay and a normal time delay with spectral info.

    # }


#----------------------------------------------------------------------
#  If the lastest update does not take effect immediately,
#  begin a loop that updates the waveform for each time sample.
#  Exit the loop when the latest update is ready to take effect.

    while accumulated_time_delay_count > 0:


#----------------------------------------------------------------------
#  Begin a loop that updates each octave's sine wave.
#  (Reminder: Python's "range" function stops one count short of the
#  specified number.)

        regenerated_audio_value = 0
        for octave in range( 1, highest_octave + 1 ):


#----------------------------------------------------------------------
#  If this octave's amplitude has changed from zero to non-zero,
#  start this octave's sine wave at the zero angle.

            if ( regeneration_amplitude_at_octave[ octave ] == 0 ) and ( amplitude_at_octave[ octave ] > 0 ):
                regeneration_amplitude_at_octave[ octave ] = amplitude_at_octave[ octave ]
                regeneration_angle_at_octave[ octave ] = 0
                regeneration_wavelength_at_octave[ octave ] = wavelength_at_octave[ octave ]
            # }


#----------------------------------------------------------------------
#  If this octave's wavelength and amplitude are waiting to be updated,
#  determine whether this sine wave has just crossed the zero value --
#  and a new non-zero amplitude is waiting.

            if ( ( ( regeneration_previous_sample_at_octave[ octave ] >= 0 ) and ( regeneration_next_previous_sample_at_octave[ octave ] <= 0 ) ) or ( ( regeneration_previous_sample_at_octave[ octave ] <= 0 ) and ( regeneration_next_previous_sample_at_octave[ octave ] >= 0 ) ) and ( amplitude_at_octave[ octave ] > 0 ) ):
                just_crossed_zero = 1
            else:
                just_crossed_zero = 0
            # }


#----------------------------------------------------------------------
#  If this sine wave has just crossed the zero value and a new non-zero
#  amplitude is waiting, update the amplitude and wavelength now.
#  This delay (waiting for a zero-value crossing) prevents a sudden
#  transition (which would insert a higher-frequency component into
#  the audio output).

            if ( just_crossed_zero == 1 ) and ( amplitude_at_octave[ octave ] > 0 ):
                regeneration_amplitude_at_octave[ octave ] = amplitude_at_octave[ octave ]
                regeneration_wavelength_at_octave[ octave ] = wavelength_at_octave[ octave ]
            # }


#----------------------------------------------------------------------
#  If this octave's sine wave is waiting to be changed to zero (and is
#  not already zero), reduce the amplitude by a proportional amount
#  each time the wave crosses the zero value.

            if ( just_crossed_zero == 1 ) and ( amplitude_at_octave[ octave ] == 0 ):
                if regeneration_amplitude_at_octave[ octave ] <= threshold_for_change_to_zero:
                    regeneration_amplitude_at_octave[ octave ] = 0
                else:
                    regeneration_amplitude_at_octave[ octave ] = regeneration_amplitude_at_octave[ octave ] * scale_for_reduction_to_zero
                # }
            # }


#----------------------------------------------------------------------
#  TO DO:  Finish debugging here.  The exponent value needs correcting.
#  The "fudge_number" needs to be removed in a way that produces the
#  correct pitch.
#  When it is correct, the pitch -- based on listening -- will match
#  the pitch of the input audio file.
#
#  Calculate how much the sine wave's angle -- in radians -- is
#  incremented for the current wavelength.

            fudge_number = -3
            increment_for_two_as_in_two_pi = 1

            angle_increment = 0
            exponent = fudge_number + increment_for_two_as_in_two_pi + bits_count_for_wavelength_at_center_of_octave + ( octave - highest_octave ) - ( regeneration_wavelength_at_octave[ octave ] * scale_for_wavelength_within_octave )
            angle_increment = ( 2 ** exponent ) * pi

#            if regeneration_amplitude_at_octave[ octave ] > 0:
#                print( "angle info: %d  %d  %d  %d  %d\n" % ( angle_increment , exponent , exponent_offset , regeneration_wavelength_at_octave[ octave ] , wavelength_at_octave[ octave ] ) )
#            # }


#----------------------------------------------------------------------
#  Update the angle for this octave's sine wave, calculate the sine
#  value for it's angle, and scale the sine-wave value according to
#  the amplitude.
#  Periodically, at intervals that are integer multiples of
#  two times pi, reset the angle to zero -- to keep the angle from
#  becoming too large a number.

            if angle_increment > 0:
                regeneration_angle_at_octave[ octave ] = regeneration_angle_at_octave[ octave ] + angle_increment
                if regeneration_angle_at_octave[ octave ] > 30:
                    regeneration_angle_at_octave[ octave ] = regeneration_angle_at_octave[ octave ] % ( 2 * pi )
                # }
            else:
                regeneration_angle_at_octave[ octave ] = 0
            # }
            contribution_at_this_octave = sin( regeneration_angle_at_octave[ octave ] ) * regeneration_amplitude_at_octave[ octave ]


#----------------------------------------------------------------------
#  Add this octave's contribution to the output waveform.

            regenerated_audio_value = regenerated_audio_value + contribution_at_this_octave

#            if regeneration_amplitude_at_octave[ octave ] > 0:
#                print( "regenerated_audio_value info: %d  %d  %d  %d  %d  %d  %d  %d\n" % ( regenerated_audio_value , contribution_at_this_octave , regeneration_angle_at_octave[ octave ] , angle_increment , regeneration_wavelength_at_octave[ octave ] , regeneration_amplitude_at_octave[ octave ] , wavelength_at_octave[ octave ] , amplitude_at_octave[ octave ] ) )
#            # }


#----------------------------------------------------------------------
#  Save the previous two values of this octave's contribution.

            regeneration_next_previous_sample_at_octave[ octave ] = regeneration_previous_sample_at_octave[ octave ]
            regeneration_previous_sample_at_octave[ octave ] = contribution_at_this_octave
          

#----------------------------------------------------------------------
#  Store the current value for this sine wave -- so that these values
#  can be plotted along with the resulting waveform.

            viewed_sample_number[ octave ] = contribution_at_this_octave


#----------------------------------------------------------------------
#  Repeat the loop to handle the next octave.

        # }


#----------------------------------------------------------------------
#  Scale the output value.
#  Also, optionally, shift the waveform amount so that the middle
#  of the waveform is not necessarily at zero.  (This allows avoiding
#  negative values.)
#  If needed to keep it within range, clip the waveform.

        scale_to_convert_amplitude_count_to_output_amplitude = 64
        wave_offset_for_output = 0
        maximum_audio_output_amplitude = max_15_bit_value

        output_audio_value = int( regenerated_audio_value * scale_to_convert_amplitude_count_to_output_amplitude ) - wave_offset_for_output

        if output_audio_value > maximum_audio_output_amplitude:
            output_audio_value = maximum_audio_output_amplitude
        elif output_audio_value < - maximum_audio_output_amplitude:
            output_audio_value = - maximum_audio_output_amplitude
        # }


#----------------------------------------------------------------------
#  Write this next sample to the audio output file.

        ( packed_value ) = struct.pack( "<h" , output_audio_value )
        compressed_audio_file.write( packed_value )


#----------------------------------------------------------------------
#  Display a text-based graphical representation of the output samples.

        scale_for_text_waveform = 0.02
        offset_count = ( len( spaces ) / 2 ) - 2

        viewed_sample_number[ 0 ] = regenerated_audio_value

        if time_counter > 0:
            list_of_characters_to_plot = "**1 2 3 4 5 6 7 8 9 a b c d e f g h "
            for sample_number in ( 0 , ):
                value_to_display = viewed_sample_number[ sample_number ]
                if ( value_to_display != 0 ) or ( sample_number == 0 ):
                    position = int( ( - value_to_display * scale_for_text_waveform ) + offset_count )
                    if ( position >= 1 ) and ( position < ( len( spaces ) - 1 ) ):
                        prefix_string = "".join( spaces[ 0 : ( position - 1 ) ] )
                        characters_to_plot = "%s%s" % ( list_of_characters_to_plot[ sample_number * 2 ] , list_of_characters_to_plot[ ( sample_number * 2 ) + 1 ] )
                        suffix_string = "".join( spaces[ ( position + 1 ) : len( spaces ) ] )
                        plot_string = "".join( [ prefix_string , characters_to_plot , suffix_string ] )
                        sys.stdout.write( ">%s<\n" % plot_string )
                    else:
                        sys.stdout.write( "[%d]\n" % ( value_to_display ) )
                    # }
                # }
            # }
        # }


#----------------------------------------------------------------------
#  Repeat the loop for the next waveform sample to generate.

        accumulated_time_delay_count = accumulated_time_delay_count - 1
        time_counter = time_counter + 1
    # }


#----------------------------------------------------------------------
#  The specified time has arrived to update an octave's amplitude
#  and wavelength, so update them.
#  Only channel one is supported here.

    amplitude_at_octave[ new_octave_number ] = new_amplitude_value
    wavelength_at_octave[ new_octave_number ] = new_wavelength_value


#----------------------------------------------------------------------
#  Repeat the loop to handle the next compressed-audio number.

# }


#----------------------------------------------------------------------
#  All done.


#----------------------------------------------------------------------
