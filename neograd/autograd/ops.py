import numpy as np
import math
from .node import Node


class Operation:
  '''
    Used when some input is getting transformed into an output, for functions
      where gradient calculation is required with the forward pass and the backward
      pass defined
  '''

  graph = None

  def __init__(self, operation, operand_needs_broadcasting):
    '''
      Params:
        operation:object(cls(Operation)) - Object of an operation that inherits Operation
        operand_needs_broadcasting:Bool - If the operand_needs_broadcasting for a pareticular
          Operation
    '''
    self.operation = operation
    self.operand_needs_broadcasting = operand_needs_broadcasting
  
  def process_operands(self, operands):
    '''
      All operands are converted to Tensor

      Params:
        operands:(any class that is supported/Tensor)
    '''
    from .tensor import Tensor
    operands = list(operands)
    for i,operand in enumerate(operands):
      if not isinstance(operand, Tensor):
        operands[i] = Tensor(operand)
    return tuple(operands)
  
  def get_tensors(self, *operands):
    '''
      Returns the processed operands as tuple of Tensors

      Params:
        operands:*args(any class that is supported/Tensor)
    '''
    tensors = self.process_operands(operands)
    if len(tensors)==0:
      return None
    elif len(tensors)==1:
      return tensors[0]
    else:
      return tensors
  
  def get_broadcast_shape(self, *tensors):
    '''
      If the tensors can be broadcasted and operand_needs_broadcasting, then the broadcasted
        shape is returned, else None
      
      Params:
        tensors:*args(Tensor)
    '''
    if self.operand_needs_broadcasting:
      try:
        return np.broadcast_shapes(*(tens.data.shape for tens in tensors))
      except ValueError:
        return None
    else:
      return None
  
  def result_requires_grad(self, tensors):
    '''
      Checks if the result requires_grad given the operands of the Operation, if atleast
        one operand requires_grad, then result will also have requires_grad
      
      Params:
        tensors:(Tensor)
    '''
    for tens in tensors:
      if tens.requires_grad:
        return True
    return False
  
  def get_result_tensor(self, result, *tensors):
    '''
      Returns the result tensor of the Operation
      Creates a Node for the result_tensor with parent_broadcast_shape and parent_needs_broadcasting
      Adds the edges to the graph

      Params:
        result:np object - Result after performing a raw numpy operation
        tensors:*args(Tensor)
    '''
    from .tensor import Tensor
    from .utils import get_graph
    graph = get_graph()
    result = result.astype(np.ndarray)
    result_tensor = Tensor(result, self.result_requires_grad(tensors))
    if graph.track:
      result_node = Node(result_tensor)
      result_node.backward_fn = self.operation.backward
      result_node.parent_broadcast_shape = self.get_broadcast_shape(*tensors)
      graph.add_edge(result_node, tensors)
    return result_tensor


# <------------ADD------------>

class Add(Operation):
  def __init__(self):
    super().__init__(self, True)

  def forward(self, tens1, tens2):
    tens1, tens2 = self.get_tensors(tens1, tens2)
    return self.get_result_tensor(tens1.data+tens2.data, tens1, tens2)

  def backward(self, tens1, tens2):
    tens1, tens2 = self.get_tensors(tens1, tens2)
    tens1.set_grad_fn(lambda ug:ug)
    tens2.set_grad_fn(lambda ug:ug)

def add(tens1, tens2):
  return Add().forward(tens1, tens2)


# <------------SUB------------>

class Sub(Operation):
  def __init__(self):
    super().__init__(self, True)
  
  def forward(self, tens1, tens2):
    tens1, tens2 = self.get_tensors(tens1, tens2)
    return self.get_result_tensor(tens1.data-tens2.data, tens1, tens2)
  
  def backward(self, tens1, tens2):
    tens1, tens2 = self.get_tensors(tens1, tens2)
    tens1.set_grad_fn(lambda ug:ug)
    tens2.set_grad_fn(lambda ug:-ug)

def sub(tens1, tens2):
  return Sub().forward(tens1, tens2)


# <------------MUL------------>

class Mul(Operation):
  def __init__(self):
    super().__init__(self, True)
  
  def forward(self, tens1, tens2):
    tens1, tens2 = self.get_tensors(tens1, tens2)
    return self.get_result_tensor(tens1.data*tens2.data, tens1, tens2)
  
  def backward(self, tens1, tens2):
    tens1, tens2 = self.get_tensors(tens1, tens2)
    broadcast_shape = self.get_broadcast_shape(tens1, tens2)
    tens1.set_grad_fn(lambda ug:tens2.data*ug)
    tens2.set_grad_fn(lambda ug:tens1.data*ug)

def mul(tens1, tens2):
  return Mul().forward(tens1, tens2)


# <------------DIV------------>

class Div(Operation):
  def __init__(self):
    super().__init__(self, True)
  
  def forward(self, tens1, tens2):
    tens1, tens2 = self.get_tensors(tens1, tens2)
    return self.get_result_tensor(tens1.data/tens2.data, tens1, tens2)
  
  def backward(self, tens1, tens2):
    tens1, tens2 = self.get_tensors(tens1, tens2)
    broadcast_shape = self.get_broadcast_shape(tens1, tens2)
    tens1.set_grad_fn(lambda ug:(1/tens2.data)*ug)
    tens2.set_grad_fn(lambda ug:((-1*tens1.data)/np.power(tens2.data, 2))*ug)

def div(tens1, tens2):
  return Div().forward(tens1, tens2)


# <------------DOT------------>

class Dot(Operation):
  def __init__(self):
    super().__init__(self, False)
  
  def forward(self, tens1, tens2):
    tens1, tens2 = self.get_tensors(tens1, tens2)
    return self.get_result_tensor(np.dot(tens1.data, tens2.data), tens1, tens2)
  
  def backward(self, tens1, tens2):
    tens1, tens2 = self.get_tensors(tens1, tens2)
    tens1.set_grad_fn(lambda ug:np.dot(ug, tens2.data.T))
    tens2.set_grad_fn(lambda ug:np.dot(tens1.data.T, ug))

def dot(tens1, tens2):
  return Dot().forward(tens1, tens2)


# <------------EXP------------>

class Exp(Operation):
  def __init__(self):
    super().__init__(self, False)
  
  def forward(self, tens):
    tens = self.get_tensors(tens)
    return self.get_result_tensor(np.exp(tens.data), tens)
  
  def backward(self, tens):
    tens = self.get_tensors(tens)
    tens.set_grad_fn(lambda ug:np.exp(tens.data)*ug)

def exp(tens):
  return Exp().forward(tens)


# <------------LOG------------>

class Log(Operation):
  def __init__(self):
    super().__init__(self, False)
  
  def forward(self, tens):
    tens = self.get_tensors(tens)
    return self.get_result_tensor(np.log(tens.data), tens)
  
  def backward(self, tens):
    tens = self.get_tensors(tens)
    tens.set_grad_fn(lambda ug:(1/tens.data)*ug)

def log(tens):
  return Log().forward(tens)


# <------------POW------------>

class Pow(Operation):
  def __init__(self):
    super().__init__(self, True)
  
  def forward(self, tens1, tens2):
    tens1, tens2 = self.get_tensors(tens1, tens2)
    return self.get_result_tensor(np.power(tens1.data, tens2.data), tens1, tens2)
  
  def backward(self, tens1, tens2):
    result = np.power(tens1.data, tens2.data)
    tens1, tens2 = self.get_tensors(tens1, tens2)
    tens1.set_grad_fn(lambda ug:(np.power(tens1.data, tens2.data-1) * tens2.data)*ug)
    tens2.set_grad_fn(lambda ug:(result*np.log(tens1.data))*ug)

def pow(tens1, tens2):
  return Pow().forward(tens1, tens2)


# <------------SUM------------>

class Sum(Operation):
  def __init__(self, axis=None):
    super().__init__(self, True)
    self.axis = axis
  
  def forward(self, tens):
    tens = self.get_tensors(tens)
    return self.get_result_tensor(np.sum(tens.data, axis=self.axis), tens)
  
  def backward(self, tens):
    tens = self.get_tensors(tens)
    
    def grad_backward(ug):
      tens_shape = list(tens.shape)
      if self.axis is not None:
        try:
          tens_shape[self.axis] = 1
        except IndexError:
          pass
        lg = 1
      else:
        lg = np.ones(tens.shape)

      if self.axis is not None:
        grads = np.dot(lg, ug)
        try:
          num_repeat = tens.shape[self.axis]
        except IndexError:
          num_repeat = 1
        grads = grads[np.newaxis]
        grads = np.concatenate([grads]*num_repeat)
      else:
        grads = lg*ug
      return grads
    tens.set_grad_fn(grad_backward)

def sum(tens, axis=None):
  return Sum(axis).forward(tens)


# <------------TRANSPOSE------------>

class Transpose(Operation):
  def __init__(self):
    super().__init__(self, False)
  
  def forward(self, tens):
    tens = self.get_tensors(tens)
    return self.get_result_tensor(tens.data.T, tens)

  def backward(self, tens):
    tens = self.get_tensors(tens)
    tens.set_grad_fn(lambda ug:ug.T)

def transpose(tens):
  return Transpose().forward(tens)


# <------------RELU------------>

class ReLU(Operation):
  def __init__(self):
    super().__init__(self, False)
  
  def forward(self, tens):
    tens = self.get_tensors(tens)
    return self.get_result_tensor(np.maximum(0, tens.data), tens)
  
  def backward(self, tens):
    tens = self.get_tensors(tens)
    tens.set_grad_fn(lambda ug:np.where(tens.data>=0, 1, 0)*ug)

def relu(tens):
  return ReLU().forward(tens)


# <------------SIGMOID------------>

class Sigmoid(Operation):
  def __init__(self):
    super().__init__(self, False)
  
  def forward(self, tens):
    tens = self.get_tensors(tens)
    return self.get_result_tensor(1/(1+np.exp(-tens.data)), tens)
  
  def backward(self, tens):
    tens = self.get_tensors(tens)
    result = 1/(1+np.exp(-tens.data))
    tens.set_grad_fn(lambda ug:(result*(1-result))*ug)

def sigmoid(tens):
  return Sigmoid().forward(tens)


# <------------TANH------------>

class Tanh(Operation):
  def __init__(self):
    super().__init__(self, False)
  
  def forward(self, tens):
    tens = self.get_tensors(tens)
    return self.get_result_tensor(np.tanh(tens.data), tens)
  
  def backward(self, tens):
    tens = self.get_tensors(tens)
    result = np.tanh(tens.data)
    tens.set_grad_fn(lambda ug:(1-np.power(result,2))*ug)

def tanh(tens):
  return Tanh().forward(tens)


# <------------CONV2D------------>

def Conv2D(Operation):
  def __init__(self, kernel, padding=0, stride=1):
    super().__init__(self, False)
    self.kernel = kernel
    self.padding = padding
    self.stride = stride
  
  def forward(self, inputs):
    inputs, self.kernel = self.get_tensors(inputs, self.kernel)
    self.validate_inputs()
    outputs = []
    padded_inputs = np.pad(inputs.data, self.padding, 'constant')
    result_shape = self.get_result_shape(inputs)
    for fragment, _, _ in self.generate_fragments(padded_inputs):
      outputs.append(np.sum(fragment*self.kernel.data))
    return self.get_result_tensor(np.array(outputs).reshape(result_shape), inputs)
  
  def backward(self, inputs):
    inputs = self.get_tensors(inputs)
    padded_inputs = np.pad(inputs.data, self.padding, 'constant')
    def grad_backward(ug):
      ug_flattened = ug.flatten()
      inputs_grads = np.zeros(padded_inputs.shape)
      for i, fragment, row_slice, col_slice in enumerate(self.generate_fragments(padded_inputs)):
        sum_grad = np.ones(self.kernel.shape)*ug_flattened[i]
        fragment_grad = self.kernel.data*sum_grad # New element wise multiplication backward algo
        kernel_grad = fragment*sum_grad # New element wise multiplication backward algo
        inputs_grads[row_slice, col_slice]+=fragment_grad
        self.kernel.grad+=kernel_grad
      unpadded_inputs_grads = self.unpad(inputs_grads)
      return unpadded_inputs_grads
    inputs.set_grad_fn(grad_backward)
  
  def generate_fragments(self, inputs_data):
    inputs_x_dim, inputs_y_dim = inputs_data.shape
    kernel_x_dim, kernel_y_dim = self.kernel.shape
    j = 0
    while(j+kernel_y_dim<=inputs_y_dim):
      i = 0
      while(i+kernel_x_dim<=inputs_x_dim):
        row_slice = slice(i, i+kernel_x_dim)
        col_slice = slice(j, j+kernel_y_dim)
        yield inputs_data[row_slice, col_slice], row_slice, col_slice
        i+=self.stride
      j+=self.stride
  
  def get_result_shape(self, inputs):
    inputs_x_dim, inputs_y_dim = inputs.shape
    kernel_x_dim, kernel_y_dim = self.kernel.shape
    def result_dim(inputs_dim, kernel_dim):
      return math.floor(((inputs_dim + (2*self.padding) - kernel_dim)/self.stride) + 1)
    result_x_dim = result_dim(inputs_x_dim, kernel_x_dim)
    result_y_dim = result_dim(inputs_y_dim, kernel_y_dim)
    return result_x_dim, result_y_dim
  
  def unpad(self, padded_data):
    padded_x_dim, padded_y_dim = padded_data.shape
    return padded_data[self.padding:padded_x_dim-self.padding, self.padding:padded_y_dim-self.padding]
  
  def validate_inputs(self, inputs):
    if len(inputs.shape)!=2:
      raise ValueError("Only 2D inputs are supported!")

def conv2d(inputs, kernel, padding, stride):
  return Conv2D(kernel, padding, stride).forward(inputs)