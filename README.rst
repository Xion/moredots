moredots (WIP)
==============

Managing dotfiles with Git and grace


Usage
-----

Initialize dotfile repository. By default, *moredots* will store them in ``~/dotfiles`` directory::

    mdots init
    # mdots init ~/dotfiles --home ~/

Add some files using ``mdots add``::

    mdots add vimrc
    mdots add .vimrc
    mdots add ~/.vimrc

*moredots* will put the originals inside the dotfile repository, while the original file is replaced
with a symbolic link::

    $ ls -al | grep vimrc
    lrwxrwxrwx  1 xion xion       26 Nov 18 02:44 .vimrc -> /home/xion/dotfiles/.vimrc

Once you added all files, synchronize them with remote Git repository, e.g. on GitHub::

    mdots sync git@github.com:Xion/dotfiles

This will pull, merge and push the files from/to designated repo. It will be remembered
as origin so later you can simply do::

    mdots sync

to synchronize any changes.
