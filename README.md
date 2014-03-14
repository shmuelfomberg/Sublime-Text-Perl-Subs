# A Sublime-Text Plugin - Perl functions listing

This plugin helps you immediately know where in the Perl file you are

If adds to the status line a small "[PerlSubs: <current>]" mark, so you know in which function you are now.

Also, upon pressing ctrl+alt+l, it opens a list of functions, and clicking on one will jump to it.

## Intallation

Drop it to your Sublime Text Plugin directory. on my computer (OSX) it is:
~/Library/Application Support/Sublime Text 2/Packages/PerlSubs

## Supported ST versions

This plugin was tested with ST2 and 3.

## TODO

Move the function name from the down-left corner to the down-right corner (where the important things are)

In the list of functions, make the package names stand out

Delayed scanning: do not scan the file immidiately on loading, nor on every change.
scan it after the loading, and two seconds after the last change

## BUGS

If the marker is below a function, but not in other function, the plugin will think that you are inside that function.
Not big deal, for me.

## License and Copyright

License: Perl Artistic 2
Copyright: Shmuel Fomberg, 2012
