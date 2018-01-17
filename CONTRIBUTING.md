Los Alamos National Laboratory policy requires that all code (new or patches) 
sign an Contributor License Agreement (CLA) to be able to submit code to 
Cinema.  No patches/pull request will be accepted without agreeing to the
Cinema CLA.

TODO: Instructions for signing the agreement via CLAHub.

Current set of rules for contributing to cinema_lib (as written by Jon W.):
1. Python 3.6 
2. SPACES, NO TABS, 80 COLUMN HARD WRAP. Check your editor. We may add 
   git-hooks to check.
3. Avoid object-oriented programming unless you feel it is required to solve
   the problem. Functions and data should be the norm. I'm likely to reject
   it if I feel it is object-oriented for no good reason.
4. Don't use anything but the standard Python library unless it is providing
   major features, and even then, the features should be optional. See
   cinema.image and cinema.ocv for examples. cinema_lib should have 
   functionality without external dependencies.
5. In general, follow PEP 8 on coding style. I personally don't like 4 spaces
   as a tab (I prefer 2), but it's better to follow community conventions.
6. Patches/pull requests are only accepted for *devel*. Except if there is a 
   major bug that requires urgent fixing. In that case, please submit a patch
   for both *master* and *devel*. Otherwise, the bug fix will come through
   merging *devel* into *master* at some point in the future.
7. Regression tests (unit tests with previously known answers) will be REQUIRED
   for ANY new code pushed to *devel*. We haven't added CI (continuous 
   integration) as of this writing, but it is planned. So you need to manually
   "python setup.py test" or "python -m unittest discover" before you push. 
   Tests reside in cinema_lib.test
8. Writing Python help (a long string at the entry point of any function,
   class, or module, i.e., “””this is a long string”””) will be REQUIRED to
   document code. Right now, I’m not focusing on a documentation tool or making
   people write their documentation in RST (which I personally hate, because
   just use Markdown for Pete’s sake). My current help looks like: 1) summary, 
   2) arguments, 3) returns, 4) side-effects. Take a look at cinema.spec.a 
   and cinema.spec.d for examples.
9. We will merge changes into *master*, from *devel*, when we feel like we 
   want to cut a new feature stable version for release. Jon W. will do a 
   merge-squash from *devel* to *master*. Please ask him if you'd like to 
   create a new feature stable version from the *devel* changes to update 
   *master*. As of this writing, there is no time-table for *master* updates.
   "git checkout master ; git merge --squash -X theirs devel ; git diff
   devel ; <fix any discrepencies between master and devel> ; git commit"

Meta-development comments for those with merge rights (and information
for non-git savvy LANL-ites):
1. DON'T MERGE UNLESS YOU REALLY KNOW WHAT YOU ARE DOING. Fixing git history
   is a pain. Read further below for more details.
2. DON'T PUSH NEW CODE TO *master* – it is supposed to be a stable branch for 
   end-users. *devel* is the branch to push new code changes to. Work on
   a feature branch to develop new code, first, and then, push to *devel* when 
   the feature branch is ready. 
3. Merge feature branches to *devel*, ONLY when the code is ready to be seen by 
   the rest of the world (i.e, feature complete). That is, should work on a 
   local branch, off of *devel*, and then merge and push it to *devel* only 
   when it’s ready. *devel* should always be semi-stable and not broken, 
   i.e., test before you push. If you need help understanding this, "branchy 
   style development", regression testing, and *git*, please talk to Jon W. 
4. DON'T PULL REQUEST/MERGE DEAD/UNCOMMENTED/UNFINISHED CODE. If it is 
   still in major development, continue to work on a feature branch before 
   merging to *devel*. Comments are reserved ONLY for explanation, not a way to 
   hide unfinished code. If a feature commit is unfinished, mark it as a WIP in 
   the git log, but ideally, try to only merge complete code in *devel* unless 
   it is a multi-stage feature commit that will take multiple branches/fixes/a 
   long time. Though, recognize doing so that slows down other developers, and
   also delays any merges to *master*.

