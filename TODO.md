- use object model when loading
- implement visitor with class-decorated visit methods
- implement layouter
  - begin with start event
    - follow all flows to tasks and build a tree like structure
      S -> T -> T
        -> T -> T
             -> T
        -> T    |
                V
                T