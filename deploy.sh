#! /bin/bash
FOLDER=/home/ste/git_repo
GIT_URL=https://github.com/StepDan23/21_roger_skyline_1.git

git clone $GIT_URL $FOLDER
cp -r $FOLDER/webpage/ .
rm -rdf $FOLDER
sudo service webpage restart
sudo service nginx restart
