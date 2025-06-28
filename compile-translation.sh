#!/bin/bash

msgfmt src/locales/ua/LC_MESSAGES/messages.po -o src/locales/ua/LC_MESSAGES/messages.mo
msgfmt src/locales/en/LC_MESSAGES/messages.po -o src/locales/en/LC_MESSAGES/messages.mo

echo "Compilation done."