/*
 *Copyright (c) 2018 Intel Corporation.
 *
 *Permission is hereby granted, free of charge, to any person obtaining a copy
 *of this software and associated documentation files (the "Software"), to deal
 *in the Software without restriction, including without limitation the rights
 *to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 *copies of the Software, and to permit persons to whom the Software is
 *furnished to do so, subject to the following conditions:
 *
 *The above copyright notice and this permission notice shall be included in
 *all copies or substantial portions of the Software.
 *
 *THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 *IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 *FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 *AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 *LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 *OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 *THE SOFTWARE.
 *
 */


%{
    #define SWIG_FILE_WITH_INIT
    #include "conv_py.h"
    #include "op_param.h"
%}

%include "param.i"
%include "conv_py.h"

%template(convolution2D) Convolution2D_Py<float>;

//
// Python API for Convolution2D
//
// mdarray Convolution2D_Py::Forward(
//                        mdarray *src, mdarray *weights,
//                        mdarray *dst, mdarray *bias,
//                        conv_param_t *cp);
// std::vector<mdarray> Convolution2D_Py::BackwardWeights(
//                        mdarray *src, mdarray *diff_dst,
//                        con_prarm_t *cp);
// mdarray Convolution2D_Py::BackwardData(
//                        mdarray *weights, mdarray *diff_dst,
//                        conv_param_t *cp);