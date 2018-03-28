import sys
import os

import htcondor


def get_pool_status(pool):
    """
    Generator that returns lines from condor about pool status

    :param pool: HTCondor pool to query
    :return: iterable with list of pools
    """
    if pool:
        cmd = 'condor_status -pool ' + pool
    else:
        cmd = 'condor_status'

    for line in os.popen(cmd, 'r'):
        yield line


def get_status(args, config):
    # htcondor bindings, param object needs more dict methods :p
    pools = [x.strip() for x in htcondor.param['flock_to'].split(',')]

    map = {}
    if config.has_section('poolnames'):
        for opt, value in config.items('poolnames'):
            try:
                key, value = value.split(',', 1)
            except ValueError:
                continue
            map[key.strip()] = value.strip()

    sys.stdout.write("Summary of available resources for all HTCondor pools:\n")
    sys.stdout.write("    Total  Owner  Claimed  Unclaimed  Matched  Preempting\n")
    for pool in [None] + pools:
        if pool:
            name = pool
        else:
            name = 'LOCAL'

        if name in map:
            name = map[name]
        sys.stdout.write("==={0}===\n".format(name))

        if args.full:
            for line in get_pool_status(pool):
                sys.stdout.write(line + "\n")
        else:
            for line in get_pool_status(pool):
                if 'Total' in line and 'Owner' not in line:
                    vals = [x.strip() for x in line.replace('Total', '').split()]
                    # as a list comprehension, vals is an iterator. Must
                    # convert to list.
                    sys.stdout.write("    %5.5s  %5.5s  %7.7s  %9.9s  %7.7s  %10.10s\n" % tuple(vals[:6]))


'''
if [[ "x$1" == "x-?" || "x$1" == "x-h" || "x$1" == "x--help" ]]; then
    echo "condor_status_all [ -f | --full]"
    exit 0
fi

if [[ "x$1" == "x-f" || "x$1" == "x--full" ]]; then
    FULL="yes"
fi

# ZEROFILL="yes"

POOLS=`condor_config_val flock_to`
#IFS=', ' read -a pools <<< "$POOLS"
arr=$(echo $POOLS | tr "," "\n")

function get_status {
    if [ "x$1" == "x" ]; then
        PARAM=""
    else
        PARAM="-pool $1"
    fi
    if [ ! -z $FULL ]; then
        condor_status $PARAM
    else
        #condor_status $PARAM | grep "Total" | grep -v "Owner" | sed "s/Total/Slots /"
        condor_status $PARAM | grep "Total" | grep -v "Owner" | sed "s/Total/     /"
        if [ $? ]; then
            [ -z $ZEROFILL ] || echo "                         0     0       0         0       0          0        0"
        fi
    fi
}
echo "Summary of available resources for all available HTCondor pools."
echo "                     Total Owner Claimed Unclaimed Matched Preempting Backfill"
echo "LOCAL POOL:"
get_status

#for i in "${array[@]}"
for i in $arr
do
    echo "POOL $i:"
    get_status $i
done
'''
