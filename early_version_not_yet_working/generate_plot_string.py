#----------------------------------------------------------------------
#
#          generate_plot_string.py
#          -----------------------
#
#  Generates a text string that horizontally displaces a specified
#  string by a distance proportional to value, where the input value
#  "value_to_plot" multiplied times "scale_for_plotting" should be
#  within the range minus one to plus one.
#
#----------------------------------------------------------------------
#  Define the function and its input values.

def generate_plot_string( value_to_plot , character_string_to_show , scale_for_plotting ):

    "Generates a text string that places a two-character text string into position based on a numeric value"


#----------------------------------------------------------------------
#  Initialization.

    spaces = [ " " for position in range( 70 ) ]
    offset_for_plotting = int( len( spaces ) / 2 )
    half_of_full_distance = offset_for_plotting - 2


#----------------------------------------------------------------------
#  Display a text-based graphical representation of the input sample,
#  plus other waveforms for debugging.

    position = int( ( value_to_plot * scale_for_plotting * half_of_full_distance ) + offset_for_plotting )
    if ( position >= 1 ) and ( position < ( len( spaces ) - 1 ) ):
        prefix_string = "".join( spaces[ 0 : ( position - 1 ) ] )
        suffix_string = "".join( spaces[ ( position + 1 ) : len( spaces ) ] )
        plot_string = "".join( [ ">" , prefix_string , character_string_to_show , suffix_string , "<" ] )
    else:
        plot_string = "[%s = %d]\n" % ( character_string_to_show , value_to_plot )
    # }


#----------------------------------------------------------------------
#  All done.

    return plot_string

# }
