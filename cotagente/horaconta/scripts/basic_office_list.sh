#!/bin/sh


[ "$F" = "" ] && F="tic.txt"


basic_list ()
{
 sed 's/Henrique Moreira/@~/g' | tr \\012 ' ' | tr @ \\012 | grep "PT "
}



#
# Main script
#

if [ "$1" ]; then
	F=$1
fi
cat $F | basic_list
RES=$?

# Exit status
exit $RES

