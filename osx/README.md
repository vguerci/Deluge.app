# Instructions for building Deluge.app

## 1. Compiler

- To build deluge and the gtk osx modules, you must use `gcc`
- This has been successfully working with :
    - gcc 4.2.1 - Xcode 4.1 - Mac OSX Lion (10.7.2)
    - llvm-gcc 4.2.1 - Xcode 4.3.1 (With Command line utilities) - Mac OSX Lion (10.7.3)
- Check your version of gcc using `gcc -v`

## 2. GTK-OSX [jhbuild][1] environment

Quick how-to *(from the full [GTK-OSX building][2] instructions)*

1. Create a dedicated user account and use it for all the next steps:

    *Note*: I'm using `gtk` login with `/opt/gtk` as home an jhbuild prefix

        sudo su - gtk
        cat << EOF > ~/.profile
        export PATH=~/.local/bin:~/bin:/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/git/bin
        EOF
        . ~/.profile

2. Download and run the [gtk-osx-build-setup][3] script to install jhbuild:

        curl -O https://raw.github.com/jralls/gtk-osx-build/master/gtk-osx-build-setup.sh
        sh gtk-osx-build-setup.sh

3. Link or copy deluge osx jhbuildrc-custom:

    *Note*: This setup builds only for `x86_64` arch to `/opt/gtk`
    prefix, feel free to edit

        ln -sf deluge/osx/jhbuildrc-custom ~/.jhbuildrc-custom

4. Build jhbuild and its modulesets: *(takes a while...)*

        jhbuild bootstrap && jhbuild

    - *Note*: If you encounter an error while building `glib` like:

            gconvert.c:65:2: error: #error GNU libiconv not in use but included iconv.h is from libiconv

        Start a shell from jhbuild (#4), edit the file `vim glib/gconvert.c +65`
        to delete the section raising error, which is irrelevant. *(Lion
        iconv.h looks like gnu one, but it is not)*
        Then exit the shell and resume build (#1)

5. Build the deluge moduleset: *(takes a while...)*

    *Note*: This jhbuild moduleset *should* build and install all deluge
    dependencies not available in gtk-osx

        jhbuild -m deluge/osx/deluge.modules build deluge

## 3. Build Deluge.app

1. Always do your custom build operations under a jhbuild shell:

        jhbuild shell

2. Cleanup:

        python setup.py clean -a

3. Build and install:

        python setup.py py2app
        python setup.py install

4. Build app to `deluge/osx/app/Deluge.app`:

        cd osx
        ./make-app.sh

You *should* have now a working Deluge.app

i386 Notes:
    - Uncomment the relevant sections of jhbuildrc-custom and deluge.modules
    - deluge egg has to be named without the -macosx-10.6-intel suffix
    - python setup.py py2app --arch=i386 *might* help
    - To build for i386 under a x64 arch libtorrent python bindings have to be
      patched manually to set correct arch see macports package patch

## Issues

If Deluge.app doesn't work or crash the first thing to do is to check OSX
Console for logs and/or crash reports. Alternatively, you can enable python
log by uncommenting the end of script `Deluge.app/Contents/MacOS/Deluge`

### Known issues

- **i386**: libtorrent crash
- **i18n**: English only for now

## Changelog

- **v1.3.3-1**: first release

- **v1.3.3-2**: **OSX integration**: [gtk-mac-integration][7]
    - Torrent files association (with a *nice* doc icon)
    - OSX MenuBar
    - OSX Accelerators: `<cmd>` instead of `<control>`

- **v1.3.3-3**:
    - Fix: Web interface bug (mako.cache missing)
    - New: i386 build (classic mode fails, libtorrent issue)
    - Updates:
        - libtorrent 0.15.8 > 0.15.9
        - Several python dependencies
        - jhbuild environment

- **v1.3.4-1**:
    - Updated to v1.3.4
    - Updated libs:
        - libtorrent 0.15.9 > 0.15.10
        - boost 1.47 > 1.49
        - openssl 1.0.0e > 1.0.0g

- **v1.3.5-1**:
    - Updated to v1.3.5

## TODO

by order of priority/feasability:

- **Notifications**: Growl

    *pynotify and pygame are not included because I don't think there is
    a way to bridge them with growl. Hopefully deluge handle this missing
    dependencies cleanly. (just logs warnings)*

- **Auto-Update**: Sparkle

    *Probably needs a native wrapper instead of the current shell script...*

## Thanks to

- The deluge team for their work.
- Winswitch team for their [osx build procedure][5] which this is largely inspired from.
- John Ralls for maintaining [gtk-osx][3] and for his [help][4].
- The py2App developers and mailing list for their [help][6].

[1]:http://live.gnome.org/Jhbuild
[2]:http://live.gnome.org/GTK%2B/OSX/Building
[3]:http://github.com/jralls/gtk-osx-build
[4]:http://sourceforge.net/apps/phpbb/gtk-osx/viewtopic.php?t=72
[5]:http://winswitch.org/dev/macosx.html
[6]:http://mail.python.org/pipermail/pythonmac-sig/2011-October/023376.html
[7]:https://github.com/jralls/gtk-mac-integration

