Current set of rules for contributing to cinema_lib:

0. SPACES, NO TABS. Check your editor.
1. In general, follow PEP 8 on coding style. I personally don't like 4 spaces
   as a tab (I prefer 2), but it's better to follow community conventions
   for open source code.
2. DON'T PUSH UNLESS YOU REALLY KNOW WHAT YOU ARE DOING. Fixing git history
   is a pain. Read further below for more details.
3. DON'T PUSH NEW CODE TO *master* – it is supposed to be a stable branch for 
   end-users. *devel* is the branch to push new code changes to.
4. Push new code to *devel*, only when your code is ready to be seen by 
   the rest of the development team. That is, you should work on a local 
   branch, off of *devel*, and then merge and push it to *devel* only when 
   it’s ready. Do not push every small change you make, especially if it 
   isn’t ready to be seen. *devel* should be semi-stable and not broken,
   i.e., test before you push "python setup.py test". If you need help 
   understanding "branchy style development" and *git*, please talk to Jon W. 
5. Regression tests (unit tests) will be REQUIRED for ANY new code (i.e., unit
   tests) pushed to *devel*. We haven't added CI (continuous integration) 
   as of this writing, but it is planned. So you need to manually
   "python setup.py test" before you push. Tests go in cinema_lib.test
6. Writing Python help (a long string at the entry point of any function,
   class, or module, i.e., “””this is a long string”””) will be REQUIRED to
   document code. Right now, I’m not focusing on a documentation tool or making
   people write their documentation in RST (which I personally hate, because
   just use Markdown for Pete’s sake). My current help looks like: 1) summary, 
   2) arguments, 3) returns, 4) side-effects. Take a look at cinema.spec.a 
   and cinema.spec.d for examples.
7. We will merge changes into *master*, from *devel*, when we feel like we 
   want to cut a new stable version for release. Jon W. will do a merge, and 
   ask him if you'd like to create a new stable version from *devel* changes.
   "git checkout master ; git merge --squash -X theirs devel ; git commit"
8. If there is a bug in *master*, fix it in *devel*, and it will get merged
   into *master* at a stable point.
9. If there is a major bug in *master* and it can’t wait – create a bug fix
   branch off of *master*, test it on *master* and *devel*, and we’ll update
   (merge into) both branches simultaneously.

