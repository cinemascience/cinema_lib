Current set of rules for contributing to cinema_lib:

1. Don’t check/push into *master* – it is supposed to be a stable branch for 
   people to use. *devel* is the branch to push code changes into.
2. Check into *devel* only when your code is ready to be seen by the rest of
   the development team. That is, you should work on a local branch, and then
   merge it into *devel* when it’s ready. Do not push every small change you
   make to “devel”, especially if it isn’t ready. *devel* should be semi-
   stable. If you need help understanding "branchy style development" and *git*,
   please talk to Jon W. Don't push if you don't know what you are doing.
3. We will merge changes into *master*, from *devel*, when we feel like we 
   want to cut a new stable version for release. Jon W. will do a merge, and 
   ask him if you'd like to create a new stable version from *devel* changes.
4. If there is a bug in *master*, fix it in *devel*, and it will get merged
   into *master* at a stable point.
5. If there is a major bug in *master* and it can’t wait – create a bug fix
   branch off of *master*, test it on *master* and *devel*, and we’ll update
   (merge into) both branches simultaneously.
6. Regression tests (unit tests) will be required. They’re not in there, as of
   this writing, but we are going to require regression testing (i.e., unit
   tests). It’s on my very next TODO so it doesn’t get thrown by the way side,
   because we need to do CI (continuous integration).
7. Writing Python help (a long string at the entry point of any function,
   class, or module, i.e., “””this is a long string”””) will be required to
   document it. Right now, I’m not focusing on a documentation tool or making
   people write their documentation in RST (which I personally hate, because
   just use Markdown for Pete’s sake, they didn’t need to reinvent Markdown).
   My current help looks like: 1) summary, 2) arguments, 3) returns, 4) 
   side-effects. Take a look at cinema.spec.a and cinema.spec.d for examples.
8. In general, follow PEP 8 on coding style. I personally don't like 4 spaces
   as a tab, but it's better to follow community conventions.
9. SPACES, NO TABS. Check your editor.
