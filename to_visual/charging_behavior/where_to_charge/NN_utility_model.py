import torch


class Net(torch.nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.l1 = torch.nn.Linear(9, 16)
        self.l2 = torch.nn.Linear(16, 32)
        self.l3 = torch.nn.Linear(32, 16)
        self.l4 = torch.nn.Linear(16, 1)
        self.relu1 = torch.nn.ReLU()
        self.relu2 = torch.nn.ReLU()
        self.relu3 = torch.nn.ReLU()
        self.relu4 = torch.nn.ReLU()

    # @torchsnooper.snoop()
    def forward(self, x):
        # x : [batch, num_station, num_feature]
        # y : [batch, num_station]
        y = []
        # for i_batch in range(x.shape[0]):
        #     tmp_batch_x = x[i_batch]
        for i in range(x.shape[1]):
            tmp_x = x[:, i].float()
            tmp_x = self.relu1(self.l1(tmp_x))
            tmp_x = self.relu2(self.l2(tmp_x))
            tmp_x = self.relu3(self.l3(tmp_x))
            tmp_x = self.relu4(self.l4(tmp_x))
            y.append(tmp_x)
        return torch.cat(y, -1)



