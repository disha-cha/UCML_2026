# CMake generated Testfile for 
# Source directory: /home/disha/UCML_2026/scip-siruil/examples/Relaxator/check
# Build directory: /home/disha/UCML_2026/scip-siruil/build/examples/Relaxator/check
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(examples-relaxator-build "/usr/bin/cmake" "--build" "/home/disha/UCML_2026/scip-siruil/build" "--target" "relaxator")
set_tests_properties(examples-relaxator-build PROPERTIES  RESOURCE_LOCK "libscip" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/examples/Relaxator/check/CMakeLists.txt;23;add_test;/home/disha/UCML_2026/scip-siruil/examples/Relaxator/check/CMakeLists.txt;0;")
add_test(examples-relaxator-enigma "/home/disha/UCML_2026/scip-siruil/build/bin/examples/relaxator" "-f" "/home/disha/UCML_2026/scip-siruil/examples/Relaxator/check/../../../check/instances/MIP/enigma.mps" "-o" "0" "0")
set_tests_properties(examples-relaxator-enigma PROPERTIES  DEPENDS "examples-relaxator-build" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/examples/Relaxator/check/CMakeLists.txt;44;add_test;/home/disha/UCML_2026/scip-siruil/examples/Relaxator/check/CMakeLists.txt;0;")
add_test(examples-relaxator-flugpl "/home/disha/UCML_2026/scip-siruil/build/bin/examples/relaxator" "-f" "/home/disha/UCML_2026/scip-siruil/examples/Relaxator/check/../../../check/instances/MIP/flugpl.mps" "-o" "1201500" "1201500")
set_tests_properties(examples-relaxator-flugpl PROPERTIES  DEPENDS "examples-relaxator-build" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/examples/Relaxator/check/CMakeLists.txt;44;add_test;/home/disha/UCML_2026/scip-siruil/examples/Relaxator/check/CMakeLists.txt;0;")
add_test(examples-relaxator-gt2 "/home/disha/UCML_2026/scip-siruil/build/bin/examples/relaxator" "-f" "/home/disha/UCML_2026/scip-siruil/examples/Relaxator/check/../../../check/instances/MIP/gt2.mps" "-o" "21166" "21166")
set_tests_properties(examples-relaxator-gt2 PROPERTIES  DEPENDS "examples-relaxator-build" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/examples/Relaxator/check/CMakeLists.txt;44;add_test;/home/disha/UCML_2026/scip-siruil/examples/Relaxator/check/CMakeLists.txt;0;")
add_test(examples-relaxator-lseu "/home/disha/UCML_2026/scip-siruil/build/bin/examples/relaxator" "-f" "/home/disha/UCML_2026/scip-siruil/examples/Relaxator/check/../../../check/instances/MIP/lseu.mps" "-o" "1120" "1120")
set_tests_properties(examples-relaxator-lseu PROPERTIES  DEPENDS "examples-relaxator-build" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/examples/Relaxator/check/CMakeLists.txt;44;add_test;/home/disha/UCML_2026/scip-siruil/examples/Relaxator/check/CMakeLists.txt;0;")
add_test(examples-relaxator-circle "/home/disha/UCML_2026/scip-siruil/build/bin/examples/relaxator" "-f" "/home/disha/UCML_2026/scip-siruil/examples/Relaxator/check/../../../check/instances/MINLP/circle.cip" "-o" "4.57424778" "4.57424778")
set_tests_properties(examples-relaxator-circle PROPERTIES  DEPENDS "examples-relaxator-build" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/examples/Relaxator/check/CMakeLists.txt;44;add_test;/home/disha/UCML_2026/scip-siruil/examples/Relaxator/check/CMakeLists.txt;0;")
add_test(examples-relaxator-m3 "/home/disha/UCML_2026/scip-siruil/build/bin/examples/relaxator" "-f" "/home/disha/UCML_2026/scip-siruil/examples/Relaxator/check/../../../check/instances/MINLP/m3.osil" "-o" "37.8" "37.8")
set_tests_properties(examples-relaxator-m3 PROPERTIES  DEPENDS "examples-relaxator-build" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/examples/Relaxator/check/CMakeLists.txt;44;add_test;/home/disha/UCML_2026/scip-siruil/examples/Relaxator/check/CMakeLists.txt;0;")
add_test(examples-relaxator-tltr "/home/disha/UCML_2026/scip-siruil/build/bin/examples/relaxator" "-f" "/home/disha/UCML_2026/scip-siruil/examples/Relaxator/check/../../../check/instances/MINLP/tltr.mps" "-o" "48.0666666667" "48.0666666667")
set_tests_properties(examples-relaxator-tltr PROPERTIES  DEPENDS "examples-relaxator-build" _BACKTRACE_TRIPLES "/home/disha/UCML_2026/scip-siruil/examples/Relaxator/check/CMakeLists.txt;44;add_test;/home/disha/UCML_2026/scip-siruil/examples/Relaxator/check/CMakeLists.txt;0;")
