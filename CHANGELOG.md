# Change log
All notable changes to this project will be documented in this file.  This
should be succinct, but still capture "what I would want co-developers to know".

This project adheres to [Semantic Versioning](http://semver.org/), but reserves
the right to do whatever the hell it wants with pre-release versioning.

Observe format below, particularly:
- version headings (with links)
- diff quick link(s) under each version heading
- project section (dir) sub-headings for each version, alphabetical with
      `Project & Toolchain` at top, then all subpackages/modules, then docs.
- type-of-change prefix for each change line
- each change only a line or 2, maybe 3 (sub-lists allowed in select cases)
- issue (not PR) link for every change line
- milestones, projects, issues, and PRs with issue linkage for each version in
      alphanumeric order
- reference-style links at very bottom of file, grouped and in completion order
- 'Unit Tests' sections only updated when async change with relevant src change
  - Otherwise assumed src changes have corresponding unit test changes

Release change log convention via
[Keep a Changelog](http://keepachangelog.com/).


---


# [Unreleased](https://github.com/JonathanCasey/grand_trade_auto/tree/develop)

Compare to [stable](https://github.com/JonathanCasey/grand_trade_auto/compare/stable...develop)


### Project & Toolchain: `.git*`, `.editorconfig`
- [Added] `.editorconfig` and `.gitattributes` added ([#26][]).
- [Added] Indent size for `.yml/.yaml` files added to `.editorconfig` ([#3][]).
- [Added] VS Code related items added to `.gitignore` ([#10][]).
- [Added] `.conf` files in `/config` added to `.gitignore` ([#2][]).
- [Added] `.gitignore` updated to exclude logger output files (unless there are
      over 1000...) ([#8][]).
- [Added] `.env` files added to `.gitignore` ([#9][]).
- [Added] EditorConifg setting for html and jinja2 files added, indent size set
      ([#11][]).
- [Added] Temporary sanitized jinja2 files added to `.gitignore` ([#11][]).
- [Added] `.coveragerc`, `.gitattributes`, `.pylintrc`, `*.conf.ci`,
      `*.conf.default`, `*.env.default`, `*.txt` added to `.editorconfig`
      ([#71][]).
- [Added] `*.conf.ci`, `*.conf.default`, `*.env.default`, `*.jinja2`, `*.svg`,
      `*.txt`, `*.yaml`, `*.yml` added to `.gitattributes` ([#71][]).
- [Added] `.editorconfig`, `.gitignore` added to `.editorconfig` ([#73][]).
- [Added] `.coveragerc`, `.editorconfig`, `.gitattributes`, `.gitignore`, and
      `.pylintrc` added to `.gitattributes` ([#73][]).


### Project & Toolchain: CircleCI
- [Added] CircleCI implemented, with `.circleci/config.yml` file that ensures
      project builds successfully ([#3][]).
- [Added] `pylint` job added to CircleCI main workflow ([#10][]).
- [Added] `pytest` job added to CircleCI main workflow ([#10][]).
- [Changed] CircleCI `main` workflow now named `lint-and-test` ([#36][]).
- [Added] Postgres image added to CircleCI with mock config file and steps to
      move into the right dir when CI run ([#2][]).
- [Added] Mock `brokers.conf` file and steps to move to properly load for Alpaca
      added to CircleCI ([#6][]).
- [Added] CircleCI workflow added for `changelog-updated`, including 3 jobs to
      check for changes to `CHANGELOG.md` ([#55][]):
  - `diff-changelog-last-commit` checks if any additions since last commit for
        develop and stable branches only.
  - `diff-changelog-vs-develop` checks if any additions compared to develop for
        non-develop branches only.
  - `find-changelog-pr-ref` checks if the current PR number shows up for PRs
        only.
- [Added] `pylint-ci_support` job added for `ci_support` dir ([#58][]).
- [Added] `init-py-checker` job added to check all `__init__.py` files are
      up to date ([#58][]).
- [Added] `PYTHONPATH` environment variable added to all python docker images
      ([#58][]).
- [Changed] Updated config file name manipulations to use `apics` instead of
      `brokers` ([#75][]).


### Project & Toolchain: CI Support
- [Added] `dir_init_checker.py` added to new `ci_support` dir to run code for
      checking `__init__.py` files are up to date ([#58][]).
- [Changed] `.circleci/*.conf.circleci` files moved and renamed to
      `ci_support/*.conf.ci` ([#58][]).
- [Changed] `brokers.conf.ci` migrated to `apics.conf.ci` ([#75][]).


### Project & Toolchain: CodeCov
- [Added] CodeCov support added to project (`.codecov.yml`) and CircleCI
      ([#13][]).
- [Added] CodeCov pass/fail criteria added ([#8][]).
- [Added] `.coveragerc` added, set to have CodeCov ignore
      `if __name__ == '__main__'` blocks since they cannot be unit tested
      ([#9][]).


### Project & Toolchain: Conventions
- [Fixed] Added pylint disable in `__init__.py` files since no module docstring
      ([#3][]).
- [Changed] Set convention to use leading `_` for class instance members only
      intended for private access ([#48][]).


### Project & Toolchain: Package, Requirements
- [Added] `requirements.txt` added, with `pylint` only entry ([#3][]).
- [Added] `pytest` being used for unit tested -- added to `requirements.txt`
      ([#10][]).
- [Added] `pytest-cov` added to `requirements.txt` ([#13][]).
- [Added] `psycopg2` added to `requirements.txt` ([#2][]).
- [Added] `alpaca-trade-api`, `numpy`, and `pandas` added to `requirements.txt`
      ([#6][]).
- [Added] `aiofiles`, `beautifulsoup4`, `fastapi`, `jinja2`, and `uvicorn` added
      to `requirements.txt` ([#11][]).


### Project & Toolchain: Pylint
- [Added] `.pylintrc` added to configure pylint, with source code paths added
      ([#4][]).
- [Added] `.pylintrc` set to always disable `logging-fstring-interpolation`, as
      it is flagging too many places where it does not matter ([#8][]).
- [Added] Good names added to `.pylintrc`, with `v` being the critical addition
      to allow usage without pylint complaints ([#9][]).
- [Added] `f` added to `good-names` list in `.pylintrc` ([#11][]).


### Project & Toolchain: Tmp Main
- [Added] `tmp_main.py` added to execute code for testing until real modules
      that will be main entry points added ([#8][]).
- [Changed] Changed `broker*` items to `apic*` items as appropriate, maintaining
      equivalent functionality ([#75][]).


### APICs / Meta
- [Added] `Apic` meta file and class started, defining initial interface
      requirements, mostly migrated from `BrokerMeta`, dropping `Meta`
      ([#75][]).
- [Changed] `get_type_names()` changed to `get_provider_names()` since `type` is
      too generic of a term, especially with future planned code ([#75][]).
- [Added] `apics` file started, loads a default main API Client handle from
      config, mostly migrated from `brokers` ([#75][]).
- [Changed] Constructor takes `kwargs`, but since this is effectively the base
      class, does nothing with it ([#75][]).
- [Changed] `_APIC_HANDLE` and other similar names shortened to `_APIC`
      ([#75][]).


### APIC: Alpaca
- [Added] `Alpaca` file and class started, with ability to load from config and
      connect, mostly migrated from `BrokerAlpaca` ([#75][]).
- [Changed] `Alpaca` constructor only explicitly takes its own args; also takes
      `kwargs` where all parent args expected, passed to `super()` constructor
      ([#75][]).


### Brokers / Meta
- [Added] `BrokerMeta` file and class started, defining initial interface
      requirements ([#6][]).
- [Added] `brokers` file started, loads a default main broker handle from
      config ([#6][]).
- [Changed] `BrokerMeta` is now simply `Broker` (still abstract) ([#75][]).
- [Changed] Inherits from `Apic` in `apic_meta` module ([#75][]).
- [Changed] Constructor takes `kwargs` to pass to `super()` constructor
      ([#75][]).
- [Changed] `load_from_config()`, `get_type_names()`, `connect()` abstract
      methods moved to `Apic` ([#75][]).
- [Removed] Removed `brokers` module for now -- replaced by `apics` ([#75][]).


### Broker: Alpaca (see APICs: Alpaca)
- [Added] `BrokerAlpaca` file and class started, with ability to load from
      config and connect ([#6][]).
- [Removed] Moved to `Alpaca` in `apic` subpackage -- see relevant changelog
      section going forward ([#75][]).


### Config: .secrets.conf
- [Added] `.secrets.conf` file created (with stub), with postgres database
      stub added ([#2][]).
- [Added] Broker example stub added, at least as would be needed for Alpaca
      ([#6][]).


### Config: .secrets.env
- [Added] `.secrets.env` file created (with stub), with email server parameters
      stub added ([#9][]).


### Config: apics.conf
- [Added] `apics.conf` file created (wtih stub) to replace `brokers.conf`,
      mostly migrated and adapted from `brokers.conf` with Alpaca at least
      supported ([#75][]).
- [Changed] `type` key changed to `provider` to avoid confusion from generic
      sounding `type` ([#75][]).


### Config: brokers.conf (see Config: apics.conf)
- [Added] `brokers.conf` file created (with stub), with Alpaca stub added
      ([#6][]).
- [Fixed] Stub text in section header now mentioned "broker" instead of
      "database" to eliminate confusion ([#59][]).
- [Removed] Moved to `apics.conf` -- see relevant changelog section going
      forward ([#75][]).


### Config: databases.conf
- [Added] `databases.conf` file created (wtih stub), with postgres stub added
      ([#2][]).


### Config: gta.conf
- [Added] `gta.conf` file created (wtih stub), with email section and parameters
      stub added ([#9][]).


### Config: logger.conf
- [Added] `logger.conf` file created (with stub), with a default ready-to-use
      logger configuration added ([#8][]).


### Databases / Meta
- [Added] `DatabaseMeta` file and class started, defining initial interface
      requirements ([#2][]).
- [Added] `databases` file started, loads a default main database handle from
      config ([#2][]).


### Database: Postgres
- [Added] `DatabasePostgres` file and class started, with ability to load from
      config, connect, create/drop/check-exists DB ([#2][]).
- [Added] Logging setup and logger usage added to existing code ([#8][]).


### General: Config
- [Added] `config.py` added with basic `ConfigParser` file loading, including
      without a section header ([#1][]).
- [Added] Default `.secrets.conf` added to `/config/stubs` with database section
      placeholder ([#2][]).
- [Added] Default `databases.conf` added to `/config/stubs` with a single
      section added for a database as a placeholder ([#2][]).
- [Changed] Now uses absolute project imports rather than relative ([#2][]).
- [Changed] Used `parser` instead of `config` as name for `ConfigParser` objects
      ([#2][]).
- [Added] `get_matching_secrets_id()` added to facilitate loading the desired
      secrets based on a provided ID ([#2][]).
- [Added] Default `logger.conf` added to `config/stubs` set to log warnings to
      file, and send split stdout/stderr between info/warning ([#8][]).
- [Added] Logger config loading and init, paired with usage of a `LevelFilter`
      and level override ability added ([#8][]).
- [Added] Logging setup and logger usage added to existing code ([#8][]).
- [Added] Default `brokers.conf` added to `config/stubs` with a single
      placeholder example ([#6][]).
- [Added] Added placeholder example for broker to default `.secrets.conf` stub
      ([#6][]).
- [Changed] Methods to load from config dropped `secrets_cp` parameter -- not
      needed ([#48][]).
- [Added] Default `.secrets.env` file added to `/config/stubs` with placeholder
      for email server options that could also be used in CLI ([#9][]).
- [Added] Default `gta.conf` file added to `/config/stubs` with placeholder for
      `[email]` section with email `recipients` ([#9][]).
- [Added] Enum and method for type casting input data added ([#9][]).
- [Added] Support for parsing a list from a config file added ([#9][]).
- [Fixed] `brokers.conf.default` now correctly references "brokers" instead of
      "databases" ([#59][]).
- [Fixed] Put file open/ops into `with` block to address new
      `consider-using-with` `pylint` finding, which also fixes it not being
      closed ([#77][]).

##### Unit Tests
- [Added] All missing unit tets for initial `config.py` work added ([#2][]).


### General: Dirs
- [Added] `dirs.py` added with basic dir resolution ([#1][]).
- [Changed] `get_src_root_path()` now named `get_src_app_root_path()` ([#32][]).
- [Added] Methods to get the jinj2 templates dir and the web frontend static dir
      ([#11][]).

##### Unit Tests
- [Added] Unit test for `test_get_root_path()` added to initially test `pytest`
      functionality ([#10][]).
- [Added] All missing units tests for initial `dirs.py` work added ([#39][]).


### General: Email Report
- [Added] Ability to load an email config and send an email implemented
      ([#9][]).
- [Added] Added main entry for `email_report` module so can call script to test
      email setup by itself ([#9][]).


### General: Exceptions
- [Added] `EmailConnectionError` and `EmailConfigError` added ([#9][]).
- [Changed] Exceptions now listed in alphabetical order ([#59][]).


### General: Utils
- [Added] `bypass_for_test()` added to allow mocking to be able to enter blocks
      of code otherwise not easily reachable, if at all ([#63][]).


### Web: Backend / Meta

##### Unit Tests: Standard
- [Added] Standard test for testing if favicon present added for use on all
      endpoints ([#11][]).


### Web: Backend: Main Web
- [Added] `main_web.py` started with `fastapi` setup, including static dir and
      jinja2 templates; and a root page added with html data example ([#11][]).


### Web: Frontend: Static: Images
- [Added] `favicon.ico` (which is really a `png`) and `gta_logo_compact.svg`
      artwork file that created it added ([#11][]).


### Web: Frontend: Templates / Meta

##### Unit Tests: Conftest
- [Added] `conftest.py` created with shared fixture to create and delete
      sanitized jinja2 template files ([#11][]).

##### Unit Tests: Standard
- [Added] Common test to check if universal style elements (stylesheets,
      scripts, etc.) are present ([#11][]).

##### Unit Tests: Utils
- [Added] Rendering of sanitized jinja2 templates either from file or from a
      string added ([#11][]).
- [Added] Sanitization of jinja2 template files for unit tests replaces
      `url_for()` elements ([#11][]).
- [Added] `extends` jinja2 blocks updated in sanitized template files to point
      to the sanitized versions of those targets for unit testing ([#11][]).
- [Added] Method for getting the path to the sanitized jinja2 templates for unit
     testing added ([#11][]).


### Web: Frontend: Templates: Main Layout
- [Added] Main layout added with icon, semantic UI style, and jinja2 blocks for
      title and body content ([#11][]).


### Web: Frontend: Templates: Root Index
- [Added] Root index page started with placeholder text for title and body
      content ([#11][]).


### Docs: CHANGELOG
- [Added] This `CHANGELOG.md` file created and updated with all project work
      to-date (+1 self reference) ([#55][]).
- [Changed] Rearranged to have subsections for `Project & Toolchain` (was
      `Repo / Toolchain`), supersection for `General` subpackage, and
      subsections for `Docs` ([#66][]).
- [Added] Note regarding the order of files here added to top bullets ([#62][],
      really [#66][]).


### Docs: CONTRIBUTING
- [Added] `CONTRIBUTING.md` added to project root; relevant parts from
      `setup.md` and `usage.md` migrated ([#62][]).


### Docs: README
- [Added] CircleCI badge for `develop` added to top of `README.md` ([#3][]).
- [Added] CodeCov badge for develop added to top of `README.md` ([#13][]).
- [Fixed] Added missing link for `usage.md` ([#67][]).
- [Added] Link to `CONTRIBUTING.md` added ([#62][]).


### Docs: Setup
- [Added] `setup.md` added with notes on setuping up CirleCI for forks ([#3][]).
- [Added] Environment setup tips added to docs ([#10][]).
- [Added] Postgres setup and config file setup added ([#2][]).
- [Added] Further environment setup tips added ([#2][]).
- [Added] Setup updated for how to use the logger config ([#8][]).
- [Added] Alpaca credential setup added to setup docs ([#6][]).


### Docs: Usage
- [Added] `usage.md` added with workflow tips ([#10][]).
- [Added] Postgres usage added ([#2][]).
- [Added] Contributing updated with why `logging-fstring-interpolation` disabled
      for pylint and what needs to be considered ([#8][]).
- [Added] Added notes on how to run main modules (`tmp_main` only for now)
      ([#45][]).
- [Added] `uvicorn` usage added ([#11][]).
- [Added] Unit testing jinja2 notes added regarding autoescape handling and
      temporary sanitized file handling ([#11][]).
- [Added] Color scheme palette added ([#11][]).


### Ref Links

#### Milestones & Projects
- [Milestone: v1.0.0](https://github.com/JonathanCasey/grand_trade_auto/milestone/1)
- [Project: v1.0.0](https://github.com/JonathanCasey/grand_trade_auto/projects/1)

#### Issues
- [#1][]
- [#2][]
- [#3][]
- [#4][]
- [#6][]
- [#8][]
- [#9][]
- [#10][]
- [#11][]
- [#13][]
- [#26][]
- [#32][]
- [#36][]
- [#39][]
- [#45][]
- [#48][]
- [#55][]
- [#58][]
- [#59][]
- [#62][]
- [#63][]
- [#66][]
- [#67][]
- [#71][]
- [#73][]
- [#75][]
- [#77][]

#### PRs
- [#29][] for [#26][]
- [#30][] for [#1][]
- [#31][] for [#4][]
- [#33][] for [#32][], related to [#1][], [#30][]
- [#34][] for [#3][]
- [#35][] for [#10][]
- [#37][] for [#36][]
- [#38][] for [#13][]
- [#40][] for [#39][]
- [#41][] for [#2][]
- [#43][] for [#8][]
- [#46][] for [#45][]
- [#47][] for [#6][]
- [#49][] for [#48][]
- [#52][] for [#9][]
- [#56][] for [#55][]
- [#60][] for [#59][]
- [#61][] for [#11][]
- [#64][] for [#63][]
- [#68][] for [#66][]
- [#69][] for [#62][], [#67][]
- [#70][] for [#58][]
- [#72][] for [#71][]
- [#74][] for [#73][]
- [#76][] for [#74][]
- [#78][] for [#77][]


---


Reference-style links here (see below, only in source) in develop-merge order.

[#26]: https://github.com/JonathanCasey/grand_trade_auto/issues/26 'Issue #26'
[#1]: https://github.com/JonathanCasey/grand_trade_auto/issues/1 'Issue #1'
[#4]: https://github.com/JonathanCasey/grand_trade_auto/issues/4 'Issue #4'
[#32]: https://github.com/JonathanCasey/grand_trade_auto/issues/32 'Issue #32'
[#3]: https://github.com/JonathanCasey/grand_trade_auto/issues/3 'Issue #3'
[#10]: https://github.com/JonathanCasey/grand_trade_auto/issues/10 'Issue #10'
[#36]: https://github.com/JonathanCasey/grand_trade_auto/issues/36 'Issue #36'
[#13]: https://github.com/JonathanCasey/grand_trade_auto/issues/13 'Issue #13'
[#39]: https://github.com/JonathanCasey/grand_trade_auto/issues/39 'Issue #39'
[#2]: https://github.com/JonathanCasey/grand_trade_auto/issues/2 'Issue #2'
[#8]: https://github.com/JonathanCasey/grand_trade_auto/issues/8 'Issue #8'
[#45]: https://github.com/JonathanCasey/grand_trade_auto/issues/45 'Issue #45'
[#6]: https://github.com/JonathanCasey/grand_trade_auto/issues/6 'Issue #6'
[#48]: https://github.com/JonathanCasey/grand_trade_auto/issues/48 'Issue #48'
[#9]: https://github.com/JonathanCasey/grand_trade_auto/issues/9 'Issue #9'
[#55]: https://github.com/JonathanCasey/grand_trade_auto/issues/55 'Issue #55'
[#59]: https://github.com/JonathanCasey/grand_trade_auto/issues/59 'Issue #59'
[#11]: https://github.com/JonathanCasey/grand_trade_auto/issues/11 'Issue #11'
[#63]: https://github.com/JonathanCasey/grand_trade_auto/issues/63 'Issue #63'
[#66]: https://github.com/JonathanCasey/grand_trade_auto/issues/66 'Issue #66'
[#67]: https://github.com/JonathanCasey/grand_trade_auto/issues/67 'Issue #67'
[#62]: https://github.com/JonathanCasey/grand_trade_auto/issues/62 'Issue #62'
[#58]: https://github.com/JonathanCasey/grand_trade_auto/issues/58 'Issue #58'
[#71]: https://github.com/JonathanCasey/grand_trade_auto/issues/71 'Issue #71'
[#73]: https://github.com/JonathanCasey/grand_trade_auto/issues/73 'Issue #73'
[#75]: https://github.com/JonathanCasey/grand_trade_auto/issues/75 'Issue #75'
[#77]: https://github.com/JonathanCasey/grand_trade_auto/issues/77 'Issue #77'

[#29]: https://github.com/JonathanCasey/grand_trade_auto/pull/26 'PR #29'
[#30]: https://github.com/JonathanCasey/grand_trade_auto/pull/30 'PR #30'
[#31]: https://github.com/JonathanCasey/grand_trade_auto/pull/31 'PR #31'
[#33]: https://github.com/JonathanCasey/grand_trade_auto/pull/33 'PR #33'
[#34]: https://github.com/JonathanCasey/grand_trade_auto/pull/34 'PR #34'
[#35]: https://github.com/JonathanCasey/grand_trade_auto/pull/35 'PR #35'
[#37]: https://github.com/JonathanCasey/grand_trade_auto/pull/37 'PR #37'
[#38]: https://github.com/JonathanCasey/grand_trade_auto/pull/38 'PR #38'
[#40]: https://github.com/JonathanCasey/grand_trade_auto/pull/40 'PR #40'
[#41]: https://github.com/JonathanCasey/grand_trade_auto/pull/41 'PR #41'
[#43]: https://github.com/JonathanCasey/grand_trade_auto/pull/43 'PR #43'
[#46]: https://github.com/JonathanCasey/grand_trade_auto/pull/46 'PR #46'
[#47]: https://github.com/JonathanCasey/grand_trade_auto/pull/47 'PR #47'
[#49]: https://github.com/JonathanCasey/grand_trade_auto/pull/49 'PR #49'
[#52]: https://github.com/JonathanCasey/grand_trade_auto/pull/52 'PR #52'
[#56]: https://github.com/JonathanCasey/grand_trade_auto/pull/56 'PR #56'
[#60]: https://github.com/JonathanCasey/grand_trade_auto/pull/60 'PR #60'
[#61]: https://github.com/JonathanCasey/grand_trade_auto/pull/61 'PR #61'
[#64]: https://github.com/JonathanCasey/grand_trade_auto/pull/64 'PR #64'
[#68]: https://github.com/JonathanCasey/grand_trade_auto/pull/68 'PR #68'
[#69]: https://github.com/JonathanCasey/grand_trade_auto/pull/69 'PR #69'
[#70]: https://github.com/JonathanCasey/grand_trade_auto/pull/70 'PR #70'
[#72]: https://github.com/JonathanCasey/grand_trade_auto/pull/72 'PR #72'
[#74]: https://github.com/JonathanCasey/grand_trade_auto/pull/74 'PR #74'
[#76]: https://github.com/JonathanCasey/grand_trade_auto/pull/76 'PR #76'
[#78]: https://github.com/JonathanCasey/grand_trade_auto/pull/78 'PR #78'
