#!/bin/sh


[ "$F" = "" ] && F="tic.txt"


basic_list ()
{
 sed 's/Henrique Moreira/@~/g' | tr \\012 ' ' | tr @ \\012 | grep " PT " | \
	sed 's/ [P-Z][A-Z]* - Vacation Leave / vacation /' | \
	sed 's/ PT - Home Office / WFO /;s/ more_horiz //;s/ \([A-Z]\)[A-Za-z]* info[ ]*$/ \1/' | \
	sed 's/Unassigned=/UN/' | \
	grep -v " Cancelled" | stripped
}


stripped ()
{
 sed 's/\([0-9][0-9-]*\) to \([0-9][0-9-]*\)/\1...\2/' | \
	awk '{printf "%s, %s\n", $6, $0}' | \
	sed 's/\.00//g'
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

