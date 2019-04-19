import torch
import torch.nn as nn
from torch.autograd import Variable

class StrongBranchNet(torch.nn.Module):
    def __init__(self, num_inputs, hidden_nodes=[50, 100, 100, 20]):
        self.linear1 = nn.Linear(num_inputs, hidden_nodes[0])
        self.linear2 = nn.Linear(hidden_nodes[0], hidden_nodes[1])
        self.linear3 = nn.Linear(hidden_nodes[1], hidden_nodes[2])
        self.linear4 = nn.Linear(hidden_nodes[2], hidden_nodes[3])
        self.linear5 = nn.Linear(hidden_nodes[3], 1)

        self.activ1 = nn.ReLU()
        self.activ2 = nn.ReLU()
        self.activ3 = nn.ReLU()
        self.activ4 = nn.ReLU()
        self.activ5 = nn.Sigmoid()

    def forward(self, input):
        x = self.activ1(self.linear1(input))
        x = self.activ2(self.linear2(x))
        x = self.activ3(self.linear3(x))
        x = self.activ4(self.linear4(x))
        x = self.activ5(self.linear5(x))
        return score


class StrongBranchMimic():
    def __init__(hyperparams=[], options=[]):
        net = StrongBranchNet(10)
        criterion = torch.nn.BCELoss()
        optimizer = torch.optim.Adam(net.parameters())

    def train_net(state):
        input = state[1]
        select_pred = net(input)
        loss = criterion(select_pred, state[2])

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
