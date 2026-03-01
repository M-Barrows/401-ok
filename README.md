<a href="https://www.hannahilea.com/blog/houseplant-programming">
  <img alt="Static Badge" src="https://img.shields.io/badge/%F0%9F%AA%B4%20Houseplant%20-x?style=flat&amp;label=Project%20type&amp;color=1E1E1D">
</a>

# 401-OK

This is a hyper-personalized application meant to facilitate my decision making around retirment contributions. I've made this with several assumptions that mirror my oppinions around investment priority (largely influenced by [The Money Guy's Financial Order of Operations (FOO)](https://moneyguy.com/guide/foo/). It is also simplified to only include the necessary complexity to model my own situation. 

# Workflow

Aside from making sure to enter all foundational information required (number of kids, state/local income tax, etc.), my typical workflow follows either of the following patterns: 

1) Enter a minimum monthly net pay amount and click the "Optimize for FOO" button. 
2) Manually adjust the contribution rates as well as salary and observe how that changes my monthly paycheck amount.

Both of these methods essentially allow me to quickly optimize an investing strategy that either sustains a certain lifestyle, targets a certain investing percentage, or perform other "what-if" investigations. 

# Potential Future Enhancements

At some point, I might incorporate some of the following features: 

* Data import/export 
* More detailed retirement balance forecast (similar to [Nerdwallet's "Retirement Calculator"](https://www.nerdwallet.com/investing/calculators/retirement-calculator)
* Tools designed to aid in planning the **during** retirement phase (similar to [Empower Retirement's planning tool](https://www.empower.com/tools/retirement-planner)
* Expanded feature set to make this tool more usefull to others

# Contributing

Largely, I will not be accepting PRs for this project as it's meant to serve just me right now. That said, if you find this tool useful and you *do* want to submit some proposed changes, please feel free to [open an issue](https://github.com/M-Barrows/401-ok/issues)! 

# Development 

> You must have Python and UV installed to run this project

Clone the repository down and run `uv run streamlit run main.py`

