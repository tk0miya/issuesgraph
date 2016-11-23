issuesgraph
===========

GitHub Issues の件数の変化を API 経由で取り出して、CSV に吐き出すツールです。
名前に graph とつけたものの、グラフ出力は Google Spreadsheet などでやってください。

Usage::

  $ export GITHUB_ACCESSTOKEN=xxxxxxx
  $ python fetch.py sphinx-doc/sphinx
  $ python convert.py
