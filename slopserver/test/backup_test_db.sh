#!/bin/bash

test_dir=slopserver/test

sqlite3 $test_dir/test_db.sqlite .dump > $1