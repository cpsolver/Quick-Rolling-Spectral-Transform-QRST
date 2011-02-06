#!/usr/bin/env python
#
#----------------------------------------------------------------------
#----------------------------------------------------------------------
#
#  Generate a signal for testing the
#  Quick Rolling Spectral Transform (QRST) algorithm.
#
#  Created by Richard Fobes, author of "The Creative Problem Solver's Toolbox"
#
#  This code is licensed under the Perl Artistic License
#  version 2.0 (see www.perlfoundation.org/artistic_license_2_0
#  or the copy included in the directory containing this code).
#
#----------------------------------------------------------------------


#----------------------------------------------------------------------
#  Specify a need for the "struct" library.
#  It is used to pack/unpack binary data written to files.

import struct


#----------------------------------------------------------------------
#  Specify a need for the math library.
#  It is needed for the "sine" function.

from math import *


#----------------------------------------------------------------------
#  Create the output file that contains audio data.

audio_file = open( 'output_binary_signal_for_testing_qrst.raw' , 'wb' , 0 )


#----------------------------------------------------------------------
#  Initialization.

time_span = 20000

amplitude_1 = 0
amplitude_2 = 0
amplitude_3 = 0
amplitude_4 = 0

angle_1 = 0
angle_2 = 0
angle_3 = 0
angle_4 = 0


#----------------------------------------------------------------------
#  Loop for each waveform sample.

for time_counter in range( time_span ):


#----------------------------------------------------------------------
#  Generate the next sample.

    offset = 2000
    amplitude_1 = 12000
    segment_length = time_span + 1
    time_count_within_segment = time_counter % segment_length
    starting_wavelength_increment = pi / 2
    ending_wavelength_increment = pi / 256
    wavelength_increment_1 = ( ( time_count_within_segment * ending_wavelength_increment ) + ( ( segment_length - time_count_within_segment ) * starting_wavelength_increment ) ) / segment_length
    angle_1 = angle_1 + wavelength_increment_1

    waveform_sample = int( offset + ( amplitude_1 * sin( ( angle_1 ) ) + ( amplitude_2 * sin( angle_2 ) ) + ( amplitude_3 * sin( angle_3 ) ) + ( amplitude_4 * sin( angle_4 ) ) ) )

    print( "t=%d  wl=%f  angle=%f  sample=%f" % ( time_counter , wavelength_increment_1 , angle_1 , waveform_sample ) )


#----------------------------------------------------------------------
#  Write to the sound file, using packed "little-endian" integer value.

    ( packed_value ) = struct.pack( "<h" , waveform_sample )
    audio_file.write( packed_value )


#----------------------------------------------------------------------
#  Repeat the loop for the next waveform sample.

# }


#----------------------------------------------------------------------
#  All done.


#----------------------------------------------------------------------
