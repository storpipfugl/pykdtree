# Releasing pykdtree

1. Add release information to README.rst
2. Update version number in setup.py
3. Commit changes
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

