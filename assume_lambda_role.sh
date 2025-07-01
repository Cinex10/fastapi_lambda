#! /bin/bash

aws sts assume-role \
    --role-arn "arn:aws:iam::471448382724:role/poshub-lambda-role" \
    --role-session-name "poshub-session"