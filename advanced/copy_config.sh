mv ~/.tmux.conf ~/.tmux.conf.backup
mv ~/.nanorc ~/.nanorc.backup
mv ~/.bash_aliases ~/.bash_aliases.backup
mv ~/.config/htop ~/.config/htop.backup
mv ~/.config/ranger ~/.config/ranger.backup

cp .tmux.conf ~/
cp .nanorc ~/
cp .bash_aliases ~/
cp .gitconfig ~/
cp -R ranger ~/.config/
cp -R htop ~/.config/
