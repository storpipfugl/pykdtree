# Releasing pykdtree

1. Add release information to README.rst
2. Update version number in setup.py
3. run `loghub` and update the `CHANGELOG.md` file and commit the changes:

   ```
   loghub storpipfugl/pykdtree --token $LOGHUB_GITHUB_TOKEN  -st $(git tag --sort=-version:refname --list 'v*' | head -n 1) -plg bug "Bugs fixed" -plg enhancement "Features added" -plg documentation "Documentation changes"
   ```

   This uses a `LOGHUB_GITHUB_TOKEN` environment variable. This must be created
   on GitHub and it is recommended that you add it to your `.bashrc` or
   `.bash_profile` or equivalent.

   This command will create a CHANGELOG.temp file which need to be added
   to the top of the CHANGLOG.md file.  The same content is also printed
   to terminal, so that can be copy-pasted, too.  Remember to update also
   the version number to the same given in step 5. Don't forget to commit
   CHANGELOG.md!

4. Create a git annotated tag by running:

   ```
   git tag -a vX.Y.Z -m "Version X.Y.Z"
   ```

5. Push to github with:

   ```
   git push --follow-tags
   ```

6. Wait for tests/actions to pass on GitHub.
7. Click "Draft a new release" at https://github.com/storpipfugl/pykdtree/releases.
   Title it "Version X.Y.Z" and include the release notes for this version in the description.

