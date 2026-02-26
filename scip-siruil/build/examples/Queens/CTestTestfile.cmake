# CMake generated Testfile for 
# Source directory: /home/disha/UCML_2026/scip-siruil/examples/Queens
# Build directory: /home/disha/UCML_2026/scip-siruil/build/examples/Queens
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(examples-queens-build "/usr/bin/cmake" "--build" "/home/disha/UCML_2026/scip-siruil/build" "--target" "queens")
set_tests_properties(examples-queens-build PROPERTIES  RESOURCE_LOCK "libscip" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/examples/Queens/CMakeLists.txt;22;add_test;/home/disha/UCML_2026/scip-siruil/examples/Queens/CMakeLists.txt;0;")
add_test(examples-queens-1 "/home/disha/UCML_2026/scip-siruil/build/bin/examples/queens" "1")
set_tests_properties(examples-queens-1 PROPERTIES  DEPENDS "examples-queens-build" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/examples/Queens/CMakeLists.txt;46;add_test;/home/disha/UCML_2026/scip-siruil/examples/Queens/CMakeLists.txt;0;")
add_test(examples-queens-2 "/home/disha/UCML_2026/scip-siruil/build/bin/examples/queens" "2")
set_tests_properties(examples-queens-2 PROPERTIES  DEPENDS "examples-queens-build" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/examples/Queens/CMakeLists.txt;46;add_test;/home/disha/UCML_2026/scip-siruil/examples/Queens/CMakeLists.txt;0;")
add_test(examples-queens-4 "/home/disha/UCML_2026/scip-siruil/build/bin/examples/queens" "4")
set_tests_properties(examples-queens-4 PROPERTIES  DEPENDS "examples-queens-build" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/examples/Queens/CMakeLists.txt;46;add_test;/home/disha/UCML_2026/scip-siruil/examples/Queens/CMakeLists.txt;0;")
add_test(examples-queens-8 "/home/disha/UCML_2026/scip-siruil/build/bin/examples/queens" "8")
set_tests_properties(examples-queens-8 PROPERTIES  DEPENDS "examples-queens-build" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/examples/Queens/CMakeLists.txt;46;add_test;/home/disha/UCML_2026/scip-siruil/examples/Queens/CMakeLists.txt;0;")
add_test(examples-queens-16 "/home/disha/UCML_2026/scip-siruil/build/bin/examples/queens" "16")
set_tests_properties(examples-queens-16 PROPERTIES  DEPENDS "examples-queens-build" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/examples/Queens/CMakeLists.txt;46;add_test;/home/disha/UCML_2026/scip-siruil/examples/Queens/CMakeLists.txt;0;")
