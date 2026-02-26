/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
/*                                                                           */
/*                  This file is part of the program and library             */
/*         SCIP --- Solving Constraint Integer Programs                      */
/*                                                                           */
/*    Copyright (C) 2002-2020 Konrad-Zuse-Zentrum                            */
/*                            fuer Informationstechnik Berlin                */
/*                                                                           */
/*  SCIP is distributed under the terms of the ZIB Academic License.         */
/*                                                                           */
/*  You should have received a copy of the ZIB Academic License              */
/*  along with SCIP; see the file COPYING. If not visit scipopt.org.         */
/*                                                                           */
/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

/**@file   scipbuildflags.c
 * @brief  build flags methods
 * @author Felipe Serrano
 */

/*---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8----+----9----+----0----+----1----+----2*/

#include "scip/scipbuildflags.h"

/** returns the flags that were used to build SCIP */
const char* SCIPgetBuildFlags(
   void
   )
{
   return " ARCH=aarch64\n\
 OSTYPE=Linux-6.6.87.2-microsoft-standard-WSL2\n\
 COMP=GNU 13.3.0\n\
 BUILD=Release\n\
 DEBUGSOL=OFF\n\
 EXPRINT=cppad\n\
 SYM=bliss\n\
 GMP=ON\n\
 IPOPT=ON\n\
 WORHP=OFF\n\
 LPS=spx\n\
 LPSCHECK=OFF\n\
 NOBLKBUFMEM=OFF\n\
 NOBLKMEM=OFF\n\
 NOBUFMEM=OFF\n\
 PARASCIP=OFF\n\
 READLINE=ON\n\
 SANITIZE_ADDRESS=OFF\n\
 SANITIZE_MEMORY=OFF\n\
 SANITIZE_UNDEFINED=ON\n\
 SANITIZE_THREAD=OFF\n\
 SHARED=ON\n\
 VERSION=7.0.2.0\n\
 API_VERSION=68\n\
 ZIMPL=ON\n\
 ZLIB=ON";
}
