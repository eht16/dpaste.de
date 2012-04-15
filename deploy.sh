#!/bin/bash

# Replace these three settings.
BASE="/srv/fastcgi"
MANAGEDIR="${BASE}/pastebin"
PROJDIR="${BASE}/pastebin/pastebin"
SOCKET="${BASE}/run/pastebin.socket"
PIDFILE="${BASE}/run/pastebin.pid"
OUTLOG="${BASE}/run/pastebin.log"
ERRLOG="${BASE}/run/pastebin_error.log"

STOP=""
GIT_PULL=""
DEPLOY=""

set -e


function stop_server
{
    if [ -f "${PIDFILE}" ]; then
        echo "--- Stop FastCGI server"
        sudo -u www-data kill `cat "${PIDFILE}"`
        rm -f "${PIDFILE}"
    fi
}


function start_server
{
    echo "--- Start FastCGI server"
    # (re)start fcgi server
    sudo -u www-data ${MANAGEDIR}/venv/bin/python \
        ${MANAGEDIR}/manage.py runfcgi \
        protocol=fcgi \
        socket="${SOCKET}" \
        pidfile="${PIDFILE}" \
        method=prefork \
        maxrequests=1000 \
        maxspare=2 \
        minspare=1 \
        maxchildren=10 \
        umask=0002 \
        workdir="${PROJDIR}" \
        debug=true \
        outlog="${OUTLOG}" \
        errlog="${ERRLOG}"
}


function activate_virtualenv
{
    echo "--- Enter virtual env"
    source ../venv/bin/activate
}


function update_static_files
{
    if [ "$DEPLOY" ]; then
        echo "--- Deploy static files"
        python manage.py collectstatic --noinput
    fi
}


function git_pull_if_necessary
{
    if [ $GIT_PULL ]; then
        echo "--- Fetch sources from GIT"
        git pull
    fi
}


cd ${PROJDIR}


while [ -n "$*" ]
do
    case $1 in
        --stop)
            STOP="1"
        ;;
        --git-pull)
            GIT_PULL="1"
        ;;
        --deploy)
            DEPLOY="1"
        ;;
    esac
    shift
done


if [ $STOP ]; then
    stop_server
    exit 0
else
    activate_virtualenv
    git_pull_if_necessary
    update_static_files
    # restart server
    stop_server
    start_server
fi

