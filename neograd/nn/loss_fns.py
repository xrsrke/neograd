from ..autograd import _sum, log


class Loss:
  def __call__(self, outputs, targets):
    return self.forward(outputs, targets)


class MSE(Loss):
  def forward(self, outputs, targets):
    num_examples = outputs.shape[-1]
    cost = (1/(2*num_examples))*_sum((outputs-targets)**2)
    return cost
  
  def __repr__(self):
    return f'MSE()'
  
  def __str__(self):
    return 'MeanSquaredError'


class BCE(Loss):
  def forward(self, outputs, targets):
    epsilon = 1e-5
    num_examples = outputs.shape[-1]
    entropy = ((outputs*log(targets+epsilon)) + ((1-outputs)*(log(1-targets+epsilon))))
    cost = (-1/num_examples)*(_sum(entropy))
    return cost
  
  def __repr__(self):
    return f'BCE()'
  
  def __str__(self):
    return 'BinaryCrossEntropy'