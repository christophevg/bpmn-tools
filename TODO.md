- add color on shape
- add lane sets
- add message flows
- add stereotypes tasks (userTask, scriptTast,...)
- implement layouter
  - begin with start event
    - follow all flows to tasks and build a tree like structure
      S -> T -> T
        -> T -> T
             -> T
        -> T    |
                V
                T
