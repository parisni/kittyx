# kittyx

Seamless workflow integration for Helix editor: Git operations, live search, file browsing, and text replacement with automatic file opening via Kitty overlay windows.

Helix's design philosophy embraces simplicity without plugins, following Unix principles of composing specialized tools. Rather than constraining functionality within Helix's limited buffer system, this project leverages Kitty terminal's powerful windowing to integrate best-in-class tools like fzf, yazi, scooter or lazygit. Each tool excels in its domain, providing capabilities no plugin could match.

## Features

| Keybinding | Mode | Description | Script |
|------------|------|-------------|---------|
| `space-g-b` | Normal | Git blame with PR/commit URLs | `kittyx-git-blame` |
| `space-g-f` | Normal | Interactive git file browser with commit history | `kittyx-tab git-file` |
| `space-g-g` | Normal | Interactive git browser (lazygit) | `kittyx-tab git` |
| `space-g-l` | Normal | Interactive git log browser | `kittyx-tab git-log` |
| `space-g-u` | Normal | Copy Git URL to clipboard (cursor line) | `kittyx-git-url-copy` |
| `space-g-o` | Normal | Open Git URL in browser (cursor line) | `kittyx-git-url-open` |
| `space-e` | Normal | File browser (yazi) - manipulate selected file | `kittyx-tab tree` |
| `space-/` | Normal | Live grep search - opens selected file | `kittyx-tab live-grep` |
| `space-/` | Select | Live grep with selected text as query - opens selected file | `kittyx-tab live-grep` |
| `space-?` | Normal | Structural search (ast-grep) - opens selected file | `kittyx-tab ast-grep` |
| `space-?` | Select | Structural search with selected text as pattern - opens selected file | `kittyx-tab ast-grep` |
| `C-S-f` | Tree | Live grep within selected folder - opens selected file | `kittyx-tab live-grep` |
| `C-S-r` | Tree | Replace text within selected folder | `kittyx-tab replace` |
| `C-S-g` | Tree | Git history for selected file/folder | `kittyx-tab git-browse` |
| `space-r` | Normal | Replace in current file | `kittyx-replace` |
| `space-R` | Normal | Replace across project | `kittyx-replace` |
| `space-r` | Select | Replace selected text in current file | `kittyx-replace` |
| `space-R` | Select | Replace selected text across project | `kittyx-replace` |
| `ctrl-space` | Kitty | View scrollback buffer in Helix overlay | `kittyx-scrollback` |
| `alt-space` | Kitty | View last command output in Helix overlay | `kittyx-scrollback` |
| `ctrl-/` | Kitty | Toggle a companion shell behind the current window | `kittens/companion.py` |
| `ctrl-shift-/` | Kitty | Close the companion shell | `kittens/companion.py close` |
| `alt-j` / `alt-k` | Kitty | Focus companion / parent, then the next window-manager window | `kittens/companion.py down` / `up` |
| `space-g-r-c` | Normal/Select | Buffer a review comment on the cursor line or selected lines | `kittyx-review comment` |
| `space-g-r-p` | Normal | Browse, edit or delete buffered review comments | `kittyx-review pending` |
| `space-g-r-f` | Normal | Post the buffered comments as one review (local: write notes), in an overlay | `kittyx-review flush --overlay` |
| `space-g-r-d` | Normal | Remove the review worktree after confirmation, in an overlay | `kittyx-review done --overlay` |

## Core Features

### Enhanced Git Blame
- **Smart PR/commit URL detection**: Automatically detects and shows PR URLs when available, falls back to commit URLs
- **Multi-platform support**: GitHub, GitLab, Bitbucket, Azure DevOps, and Gerrit
- **Platform-specific patterns**: Recognizes different PR formats (`#123` for GitHub, `!123` for GitLab, Change-Id for Gerrit)
- **Rich output**: Shows author, time since commit, commit message, and clickable URL
- **URL-only mode**: `--url-only` flag for integration with other tools

### Git Browser Integration
- **Lazygit integration**: Full-featured git interface in an overlay over Helix
- **Open from lazygit**: with `--open-in-helix`, lazygit's edit (`e`) closes the overlay and opens the file at the selected line in Helix
- **Git log browser**: Interactive commit history with fzf
- **Modified files browser**: Interactive browser for git status files


### File Browser (Yazi Integration)
- **Interactive file browser**: Full-featured yazi file manager in an overlay over Helix
- **Smart directory detection**: Opens from current buffer's directory or specified path
- **Seamless file opening**: Selected files automatically open in Helix after the overlay closes
- **Live grep integration**: Press `Shift+Ctrl+F` in yazi to search within the current directory
- **Unified workflow**: Both yazi selection and live-grep from yazi work seamlessly together

![](https://github.com/user-attachments/assets/1f1ca9cf-cce1-420c-960e-1a383e7cc341)

### Live Grep Search
- Interactive ripgrep with fzf interface in an overlay over Helix
- ripgrep runs on the typed query (fixed string, smart case, 3 chars minimum), so large repos are never piped whole into fzf
- Closest matches first: searches the current buffer's directory, then each parent up to the git root (`--start-from`)
- `ctrl-t` toggles between ripgrep and fzf filtering of the current results
- Copy file:line references with `ctrl-y`
- Selection mode prepopulates search query
- **Seamless file opening**: Selected files automatically open in Helix after the overlay closes
- Rich syntax highlighting in preview
- Single file selection only (no multi-select)

![](https://github.com/user-attachments/assets/2e894dad-2d8a-4973-a833-ae020e7bafd5)

### Structural Search (ast-grep)

Where live grep matches *text*, this matches *code shape*. You write a snippet in
the target language with metavariables standing in for the parts you don't care
about, so `$A($$$ARGS)` finds every call regardless of name or argument count —
no regex gymnastics, no matches inside comments or strings.

- `$A` — exactly one node (an expression, an identifier, an argument). Named, so
  `bar($A, $A)` requires both to be identical.
- `$$$ARGS` — zero or more nodes (an argument list, a function body). Bare `$$$`
  works too, except on its own.
- The pattern must be syntactically complete: `foo(` matches nothing, `foo($$$)`
  works. Incomplete patterns while typing simply yield an empty list.

The search re-runs on each keystroke once the query reaches 3 characters
(`--min-chars`), since a shorter pattern matches nearly every node. The language
is inferred from the file extension; add a `lang:` token to the query to restrict
it, as in `$A.$B($$$C) lang:java,py`. Markdown files are excluded — its grammar
has no call expressions, so any pattern would match arbitrary prose.

Beware that ast-grep matches a syntactic shape, not text: `check($A)` finds calls
only, never the `def check(x)` that declares it, and it excludes both `check()`
and `obj.check(x)`. Use `def check($A): $$$B` for the declaration and
`$X.check($$$)` for method calls.

Requires the [ast-grep](https://ast-grep.github.io) binary, invoked as
`ast-grep`: the short `sg` alias collides with the setgid `sg` from
shadow-utils. Full pattern reference: the
[syntax guide](https://ast-grep.github.io/guide/pattern-syntax.html) and
[playground](https://ast-grep.github.io/playground.html).

### Text Replacement (Scooter Integration)
- **File-scoped replacement**: Replace in current file with interactive preview
- **Project-wide replacement**: Replace across entire project with scooter integration
- **Selection-aware**: Works with selected text in Helix

### Scrollback Viewer
- **Terminal scrollback integration**: View terminal scrollback buffer in Helix overlay
- **Command output viewer**: View last command output in Helix overlay  
- **Smart cursor positioning**: Positions at cursor location for vim/less windows, jumps to end for other content
- **Custom keybindings**: Inherits your Helix config with added `q` key for force quit
- **Fast temporary files**: Uses `/dev/shm` when available (falls back to `$TMPDIR` on macOS)


### Markdown Preview
- **Live preview**: Converts markdown to HTML with automatic browser opening
- **GitHub styling**: Uses GitHub markdown CSS for consistent appearance
- **Isolated serving**: Each markdown file gets its own preview directory
- **Live reload**: Uses live-server for automatic refresh on changes
- **Pandoc integration**: Full-featured markdown conversion with self-contained HTML

![](https://github.com/user-attachments/assets/12467ce3-d1be-4346-b084-5a60651699f5)

### Companion Shell
- **Hidden layer**: one shell per window (e.g. Helix), in the same tab; with the
  `stack` layout only one of the two is visible, `ctrl-/` flips between them
- **Right directory**: starts in the parent's working directory (`--cwd=current`)
- **Window-manager agnostic**: lives inside kitty, so it works the same on
  Linux (sway/i3) and macOS
- **Pair-aware focus**: `alt-j` goes from the parent to its companion and
  `alt-k` back; past that edge (or without a companion) the kitten runs
  `swaymsg`/`i3-msg focus down|up`, so these keys must not be bound in sway/i3
- **Discoverable**: tagged with the `kittyx_companion=<parent window id>` user
  variable, so other tools (e.g. dfzf) can list or target it

### Code Review (GitHub, GitHub Enterprise, Gerrit and local branches)
- **Three forges**: github.com and GitHub Enterprise pull requests
  (`https://<host>/<owner>/<repo>/pull/<N>`, through `gh`), Gerrit changes
  (`https://<host>/c/<project>/+/<N>`, through the REST API and `~/.netrc`)
- **Offline-first**: `kittyx-review open <url>` checks the PR or change out in a
  worktree reset to its base, so lazygit shows the whole change as unstaged and
  every file is at the reviewed version; the base is what the forge shows (the
  PR merge-base, the change parent), `--last` narrows a PR to its head commit
- **Refresh**: re-running `open` on a newer head or patchset moves the worktree
  when no comment is buffered, otherwise it warns `STALE`
- **Comment from Helix**: the Helix line *is* the line to comment on;
  `space-g-r-c` edits the body in a kitty overlay and buffers it as JSON in
  `<worktree>/.gh-review-pending/`, nothing is posted yet
- **One grouped review**: `kittyx-review flush` posts every buffered comment and
  the verdict at once (`COMMENT`, `APPROVE`, `REQUEST_CHANGES`; Gerrit votes
  `Code-Review +2` / `-2`), `--dry-run` prints the payload
- **Safe anchors**: GitHub comments off the PR net diff and Gerrit lines past the
  end of the file stay in the buffer instead of breaking the review
- **Bookkeeping**: `ls` lists the reviews in progress and their unposted
  comments, `done` removes a flushed one
- **Agent friendly**: `open --no-tab`, `ls --json`,
  `comment --body-file` and `flush --event` run without a terminal
- **Local branches**: `kittyx-review local [<branch>] [--base <ref> | --last]` reviews a
  committed branch of the current repo against its merge-base with
  `origin/HEAD` (or its head commit only); `flush` writes the comments as markdown notes, and
  `kittyx-review notes`, run from the dev repo, prints those not read yet so the
  agent that wrote the branch can address them

```bash
kittyx-review open https://github.com/owner/repo/pull/123      # opens a lazygit tab
kittyx-review open https://ghe.example.com/owner/repo/pull/45
kittyx-review open https://review.example.com/c/project/+/6789
kittyx-review flush --dry-run             # from inside the review worktree
kittyx-review flush --event APPROVE
kittyx-review done

kittyx-review local                       # current branch, from the dev repo
kittyx-review flush                       # from the review worktree: writes notes.md
kittyx-review notes                       # from the dev repo: unread notes
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/parisni/kittyx.git
   ```

2. Add the `bin/` directory to your PATH:
   ```bash
   export PATH="$PATH:/path/to/kittyx/bin"
   ```

3. Add the key mappings to your Helix `config.toml`:

## Configuration

Add the following key mappings to your Helix configuration file (`~/.config/helix/config.toml`):

```toml
[keys.normal.space]
# Live grep search with automatic file opening
"/" = [":open %sh{kittyx-tab live-grep --start-from '%{buffer_name}'}"]

# Structural search (ast-grep) with automatic file opening
"?" = [":open %sh{kittyx-tab ast-grep}"]

# Git operations
g = { "b" = ":sh kittyx-git-blame %{buffer_name} %{cursor_line}", "f" = ":sh kittyx-tab git-file %{buffer_name}", "l" = ":sh kittyx-tab git-log", "u" = ":sh kittyx-git-url-copy %{buffer_name} %{cursor_line}", "o" = ":sh kittyx-git-url-open %{buffer_name} %{cursor_line}", "g" = ":sh kittyx-tab git" }

# File browser with automatic file opening
e = ":open %sh{kittyx-tab tree '%{buffer_name}'}"


# Text replacement
R = [ ":write-all", ":sh kittyx-tab replace", ":reload-all" ]
r = [ ":write-all", ":sh kittyx-tab replace %{buffer_name}", ":reload-all" ]

[keys.select.space]
# Live grep with selected text as query  
"/" = [":pipe tee /tmp/kittyx-live-grep-query", ":open %sh{kittyx-tab live-grep --start-from '%{buffer_name}'}"]

# Structural search with selected text as pattern
"?" = [":pipe tee /tmp/kittyx-ast-grep-query", ":open %sh{kittyx-tab ast-grep}"]

# Text replacement with selection
r = [ ":pipe tee /tmp/kittyx-replace.tmp", ":sh kittyx-tab replace %{buffer_name}", ":reload-all" ]
R = [ ":pipe tee /tmp/kittyx-replace.tmp", ":sh kittyx-tab replace", ":reload-all" ]
```

### Kitty Configuration

Add the following to your Kitty configuration file (`~/.config/kitty/kitty.conf`):

```bash
# Scrollback viewer with Helix
map ctrl+space launch --type=overlay --title=current --stdin-source=@screen_scrollback kittyx-scrollback
map alt+space launch --type=overlay --title=current --stdin-source=@last_cmd_output kittyx-scrollback

# Companion shell (needs the stack layout; kittens run inside kitty, no remote control required)
enabled_layouts stack
map ctrl+slash       kitten /path/to/kittyx/kittens/companion.py
map ctrl+shift+slash kitten /path/to/kittyx/kittens/companion.py close
# Replaces the WM's alt+j/alt+k focus bindings (remove those from sway/i3)
map alt+j kitten /path/to/kittyx/kittens/companion.py down
map alt+k kitten /path/to/kittyx/kittens/companion.py up
```

### Lazygit Configuration

To open files from lazygit (`e`) in the calling Helix, call `git-browse` with `--open-in-helix` through `:open`, e.g. `"g" = ":open %sh{kittyx-tab git-browse --open-in-helix --status}"`, and add to `~/.config/lazygit/config.yml`:

```yaml
os:
  edit: 'kittyx-git-edit -- {{filename}}'
  editAtLine: 'kittyx-git-edit --line {{line}} -- {{filename}}'
  editInTerminal: true
```

Outside `--open-in-helix` (lazygit started elsewhere), `kittyx-git-edit` opens the files in `hx`.

### Review Configuration

Review keys for Helix (`space-g-r` must not clash with another `space-g` binding):

```toml
[keys.normal.space.g.r]
c = ":sh kittyx-review comment %{buffer_name} %{selection_line_start} %{selection_line_end}"
p = ":open %sh{kittyx-review pending --open-in-helix %{buffer_name}}"
f = ":sh kittyx-review flush --overlay %{buffer_name}"
d = ":sh kittyx-review done --overlay %{buffer_name}"

[keys.select.space.g.r]
c = ":sh kittyx-review comment %{buffer_name} %{selection_line_start} %{selection_line_end}"
```

Paths go in `~/.config/kittyx/review.conf` (sourced as bash, every key optional);
hosts come from the review URL:

```bash
GERRIT_USER=$USER                       # ssh user of the Gerrit clone hint
REVIEW_WORKTREE_ROOT=~/.local/share/kittyx/reviews
REPO_ROOTS="$HOME/git"                  # local clones: <root>/<repo name>
```

`open` adds a worktree to the local clone whose `origin` matches the review; it
never clones by itself.

### Yazi Configuration

For enhanced yazi integration, add the following to your yazi keymap configuration file (`~/.config/yazi/keymap.toml`):

```toml
[[mgr.prepend_keymap]]
on   = "<S-C-f>"
run  = 'shell -- kittyx-tab live-grep --open-in-helix --quit-tree --filepath %h'
desc = "Live grep on the given folder"

[[mgr.prepend_keymap]]
on   = "<S-C-r>"
run  = 'shell -- kittyx-tab replace --quit-tree --filepath %h'
desc = "Replace text in the given folder"

[[mgr.prepend_keymap]]
on   = "<S-C-g>"
run  = 'shell -- kittyx-tab git-browse --filepath %h'
desc = "Git history for the selected file/folder"
```

This enables:

- **`Shift+Ctrl+F` in yazi**: Launch live grep search in the current directory
- **`Shift+Ctrl+R` in yazi**: Launch text replacement in the current directory
- **`Shift+Ctrl+G` in yazi**: View git history for the selected file/folder
- **Automatic integration**: Search results open directly in Helix, replacements work within selected directory
- **Smart cleanup**: Yazi automatically closes after file selection

## Requirements
- [Helix Editor](https://helix-editor.com/)
- [Kitty Terminal](https://sw.kovidgoyal.net/kitty/)
- [fzf](https://github.com/junegunn/fzf)
- [ripgrep](https://github.com/BurntSushi/ripgrep)
- [ast-grep](https://ast-grep.github.io) (for structural search)
- [bat](https://github.com/sharkdp/bat) (for syntax highlighting in preview)
- [jq](https://github.com/jqlang/jq) (for JSON processing)
- [lazygit](https://github.com/jesseduffield/lazygit)
- [gh](https://cli.github.com/) and curl (for `kittyx-review`; bash 4+)
- [scooter](https://github.com/thomasschafer/scooter)
- [yazi](https://github.com/sxyazi/yazi)
