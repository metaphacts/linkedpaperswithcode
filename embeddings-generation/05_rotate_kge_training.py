#script to calculate RotatE embeddings for the entities and relations of the linkedpaperswithcode dataset
import torch
from torch_geometric.data import Dataset, download_url, Data
from torch_geometric.transforms import RandomLinkSplit
from torch_geometric import seed_everything
from torch_geometric.nn import RotatE
import torch
import torch.optim as optim
import time

#path to the output evaluation file
with open(".../rotate-kge-summary.txt", "w",) as z:
    start_time = time.ctime()
    z.write(f'Calculate embeddings with RotatE started at: {start_time}\n')
    z.flush()
    print('Calculate embeddings with RotatE started at: ', start_time)

    first_numbers = []
    second_numbers = []
    third_numbers = []

    #input dataset
    with open('.../triples.txt', 'r') as file:
        for line in file:
            numbers = line.split()
            first_numbers.append(int(numbers[0]))
            second_numbers.append(int(numbers[1]))
            third_numbers.append(int(numbers[2]))

    # Konvertiere die Listen in PyTorch-Tensoren
    first_tensor = torch.tensor(first_numbers)
    second_tensor = torch.tensor(second_numbers)
    third_tensor = torch.tensor(third_numbers)

    # Kombiniere die beiden Tensoren in einem 2D-Tensor
    combined_tensor = torch.stack((first_tensor, third_tensor))

    data = Data(edge_index=combined_tensor,
                edge_type=second_tensor,
                num_nodes=combined_tensor.max().item() + 1,
                ) 

    seed_everything(1)
    transform = RandomLinkSplit(
        num_val=0.1,
        num_test=0.1,
    )
    train_data, val_data, test_data = transform(data)

    #device = torch.device('cuda:0') 
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    z.write(f'Using device: {device}\n')
    z.flush()
    print('Using device:', device)

    model = RotatE(
        num_nodes=train_data.num_nodes,
        num_relations=train_data.num_edge_types,
        hidden_channels=256,
    ).to(device)

    loader = model.loader(
        head_index=train_data.edge_index[0].to(device),
        rel_type=train_data.edge_type.to(device),
        tail_index=train_data.edge_index[1].to(device),
        batch_size=2000,
        shuffle=True,
    )

    optimizer = optim.Adam(model.parameters(), lr=0.001)

    def train():
        model.train()
        total_loss = total_examples = 0
        for head_index, rel_type, tail_index in loader:
            optimizer.zero_grad()
            loss = model.loss(head_index, rel_type, tail_index)
            loss.backward()
            optimizer.step()
            total_loss += float(loss) * head_index.numel()
            total_examples += head_index.numel()
        return total_loss / total_examples


    @torch.no_grad()
    def test(val_data, k):
        model.eval()
        head_index = val_data.edge_index[0].to(device)
        rel_type = val_data.edge_type.to(device)
        tail_index = val_data.edge_index[1].to(device)
        return model.test(
            head_index=head_index,
            rel_type=rel_type,
            tail_index=tail_index,
            batch_size=20000,
            k=k,
        )


    for epoch in range(1, 301):
        loss = train()
        z.write(f'Epoch: {epoch:03d}, Loss: {loss:.4f}\n')
        z.flush()

    
    k_values = [1, 3, 10]
    results = {}
    for k in k_values:
        results[k] = test(test_data, k)

    for k in k_values:
        rank, hits_at_k = results[k]
        z.write(f'Test Mean Rank: {rank:.2f}, Test Hits@{k}: {hits_at_k:.4f}\n')
        z.flush()

    end_time = time.ctime()
    z.write(f'Calculate embeddings with RotatE end at: {end_time}\n')
    z.flush()
    print('Calculate embeddings with RotatE end at: ', end_time)

print('Done')