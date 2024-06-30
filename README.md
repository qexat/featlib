# featlib

A library to manage optional features in other projects.

## What is it for?

Let's say you are building `foo`, a command line interface. You want to add an optional feature that allows the user to make the interface full screen. You remember that there is a package `bar` that already provides it, so instead of rewriting it yourself, you want to use that piece of code. So far, it's simple: you add the line `bar = ["bar"]` in the `project.optional-dependencies` of your `pyproject.toml`.

However, when it comes to the actual implementation of making the feature optionally available, it becomes more complicated, especially if your project is tested against a static type checker or a test framework.

`featlib` tries to remediate this issue, and provides a set of utilities to use in such projects.
