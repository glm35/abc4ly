#!/bin/bash

set -e
#set -x

ME=$(basename "$0")

ABC4LY_BASE_DIR=${HOME}/doc/.perso/abc4ly

# ----------------------------------------------------------------------------
# Configuration options
# (setable with command line parameters)
# ----------------------------------------------------------------------------

VERBOSE=no

# ----------------------------------------------------------------------------
# Script usage
# ----------------------------------------------------------------------------

show_usage()
{
    cat <<EOF
$ME - Do this and that
Usage:
    $ME [OPTIONS]

OPTIONS
    -h: show this help message
    -v: be verbose
    -d: debug mode (set -x)
EOF
}

# ----------------------------------------------------------------------------
# Parse command line options and configure the script
# ----------------------------------------------------------------------------

function configure
{
    while getopts ":vhd" opt; do
        case $opt in
            v)
                VERBOSE=yes
                ;;
            h)
                show_usage
                exit 0
                ;;
            d)
                set -x
                ;;
            
            ?)
                show_usage
                exit 1
                ;;
        esac
    done
    
    if [ $VERBOSE == yes ]; then
        cat <<EOF
Configuration for $ME:
    VERBOSE = $VERBOSE
EOF
    fi
}

# ----------------------------------------------------------------------------
# The main program
# ----------------------------------------------------------------------------

configure $*
shift $(($OPTIND-1))

cd $ABC4LY_BASE_DIR
[ -d tmp ] || mkdir -p tmp

cat <<EOF > tmp/abc4ly.screen.rc 
source ${HOME}/.zeugma/etc/screen/screenrc
screen -t ipython ipython
screen -t abc4ly
chdir ${ABC4LY_BASE_DIR}/regression
screen -t regression
select 1
EOF

screen -c ${ABC4LY_BASE_DIR}/tmp/abc4ly.screen.rc

exit 0

# ----------------------------------------------------------------------------
# Text editor tab configuration
# ----------------------------------------------------------------------------

# Local Variables:
# mode: sh
# tab-width: 4
# sh-basic-offset: 4
# sh-indentation: 4
# indent-tabs-mode: nil
# End:
# (the following line needs "set modeline" in .vimrc):
# vim:expandtab:tabstop=4 softtabstop=4 shiftwidth=4
