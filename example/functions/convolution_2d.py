import numpy
import unittest

import chainer

from chainer import function_node
from chainer.utils import type_check

from ideep import xnn


def _pair(x):
    if hasattr(x, '__getitem__'):
        return x
    return x, x


class Convolution2DFunction(function_node.FunctionNode):

    def __init__(self, stride=1, pad=0, cover_all=False):
        self.sy, self.sx = _pair(stride)
        self.ph, self.pw = _pair(pad)
        self.cover_all = cover_all

    def check_type_forward(self, in_types):
        n_in = in_types.size()
        type_check.expect(2 <= n_in, n_in <= 3)

        x_type = in_types[0]
        w_type = in_types[1]
        type_check.expect(
            x_type.dtype.kind == 'f',
            w_type.dtype.kind == 'f',
            x_type.ndim == 4,
            w_type.ndim == 4,
            x_type.shape[1] == w_type.shape[1],
        )

        if type_check.eval(n_in) == 3:
            b_type = in_types[2]
            type_check.expect(
                b_type.dtype == x_type.dtype,
                b_type.ndim == 1,
                b_type.shape[0] == w_type.shape[0],
            )

    def forward_cpu(self, inputs):
        if len(inputs) == 3:
            self.retain_inputs((0, 1, 2))
        else:
            self.retain_inputs((0, 1))

        cc = xnn.ConvolutionForward(
            inputs, stride=(self.sy, self.sx),
            pad=(self.ph, self.pw), cover_all=self.cover_all,
            pos=(0, 0))

        self.hint = cc.hint
        self.W = cc.W

        y, = cc.execute_on()
        y.reset_buf_order()

        return y,

    def backward(self, indexes, grad_outputs):
        inputs = self.get_retained_inputs()
        gy, = grad_outputs

        ret = []
        if 0 in indexes:
            pass

        if 1 in indexes:
            gW_b = Convolution2DGradW(self).apply((x, gy))
            ret.append(gW_b[0])

            if 2 in indexes:
                ret.append(gW_b[1])

        return ret

class Convolution2DGradW(function_node.FunctionNode):

    def __init__(self, conv2d):
        W_node = conv2d.inputs[1]
        self.kh, self.kw = W_node.shape[2:]
        self.sy = conv2d.sy
        self.sx = conv2d.sx
        self.ph = conv2d.ph
        self.pw = conv2d.pw
        self.cover_all = conv2d.cover_all
        self.W_dtype = W_node.dtype
        self.hint = conv2d.hint

    def forward_cpu(self, inputs):
        self.retain_inputs((0, 1))

        cc = xnn.ConvolutionBackwardWeights(
            inputs, self.hint, stride=(self.sy, self.sx),
            pad=(self.ph, self.pw), cover_all=self.cover_all,
            pos=(self.rank, self.fanout))

        gW_b = cc_weight.execute_on()

    def backward(self, indexes, grad_outputs):
        x, gy = self.get_retained_inputs()
        ggW, = grad_outputs

        ret = []
        if 0 in indexes:
            pass
        if 1 in indexes:
            ggy = convolution_2d(
                x, ggW, stride=(self.sy, self.sx)
                pad=(self.ph, self.pw), cover_all=self.cover_all)
            ret.append(ggy)

        return ret


def convolution_2d(
    x, W, b=None, stride=1, pad=0, cover_all=False, **kwargs):
    fnode = Convolution2DFunction(stride, pad, cover_all)
    if b is None:
        args = x, W
    else:
        args = x, W, b
    y, = fnode.apply(args)
    return y
