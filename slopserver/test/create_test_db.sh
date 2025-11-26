#!/bin/bash

test_dir=slopserver/test

cat $test_dir/test_db.sql | sqlite3 $test_dir/test_db.sqlite