# ICT2103_RentalAndResaleHousing

- the mariadb connection gets connection details from dbconnection.txt
after you pull my recent codes, yall should first run 
git update-index --skip-worktree dbconnection.txt in your terminal
then when you change stuff in the text file like your password etc, it shouldnt show up in the staged changes bar no matter how much you change it
but make sure to do that git command first before you make any changes to the txt file
the rows in dbconnection correspond to:
line 1: 127.0.0.1 (host)
line 2: 3306 (port)
line 3: root (user)
line 4: root (password)
line 5: RnRHousing (database name)
