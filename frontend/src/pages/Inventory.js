import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Chip,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Edit as EditIcon,
  Add as AddIcon,
  Warning as WarningIcon,
  Inventory as InventoryIcon,
} from '@mui/icons-material';
import { DataGrid } from '@mui/x-data-grid';
import { inventoryAPI, restocksAPI, itemsAPI } from '../services/api';

function Inventory() {
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [restockDialogOpen, setRestockDialogOpen] = useState(false);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [items, setItems] = useState([]);
  const [areas, setAreas] = useState([]);
  const [formData, setFormData] = useState({
    quantity: 0,
    threshold: 0,
    safety_stock: 0,
  });
  const [addFormData, setAddFormData] = useState({
    item_id: '',
    area_id: '',
    quantity: 0,
    threshold: 0,
    safety_stock: 0,
  });
  const [restockForm, setRestockForm] = useState({
    quantity_requested: 0,
  });

  useEffect(() => {
    fetchInventory();
    fetchItems();
    fetchAreas();
  }, []);

  const fetchItems = async () => {
    try {
      const response = await itemsAPI.getAll();
      setItems(response.data || []);
    } catch (err) {
      console.error('Items error:', err);
    }
  };

  const fetchAreas = async () => {
    try {
      // Get unique areas from inventory data
      const response = await inventoryAPI.getAll();
      const inventoryData = response.data || [];
      const uniqueAreas = [...new Set(inventoryData.map(inv => inv.area_id))];
      
      // Add some additional areas for new inventory items
      const additionalAreas = [22, 23, 24, 25]; // Additional area IDs
      const allAreas = [...new Set([...uniqueAreas, ...additionalAreas])];
      
      setAreas(allAreas.map(id => ({ id, name: `Area ${id}` })));
    } catch (err) {
      console.error('Areas error:', err);
    }
  };

  const fetchInventory = async () => {
    try {
      setLoading(true);
      const response = await inventoryAPI.getAll().catch(() => ({ data: [] }));
      setInventory(response.data || []);
    } catch (err) {
      setError('Failed to fetch inventory data');
      console.error('Inventory error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleEditClick = (item) => {
    setSelectedItem(item);
    setFormData({
      quantity: item.quantity,
      threshold: item.threshold,
      safety_stock: item.safety_stock || 0,
    });
    setEditDialogOpen(true);
  };

  const handleSave = async () => {
    try {
      await inventoryAPI.update(selectedItem.id, formData);
      setEditDialogOpen(false);
      fetchInventory();
    } catch (err) {
      setError('Failed to update inventory item');
      console.error('Update error:', err);
    }
  };

  const handleRequestRestock = (item) => {
    setSelectedItem(item);
    setRestockForm({
      quantity_requested: Math.max(item.threshold - item.quantity, 10)
    });
    setRestockDialogOpen(true);
  };

  const handleSaveRestock = async () => {
    try {
      if (!restockForm.quantity_requested || restockForm.quantity_requested <= 0) {
        setError('Please enter a valid quantity');
        return;
      }
      
      const restockData = {
        inventory_id: selectedItem.id,
        item_id: selectedItem.item_id,
        area_id: selectedItem.area_id,
        quantity_requested: restockForm.quantity_requested,
        status: 'requested'
      };
      await restocksAPI.create(restockData);
      setRestockDialogOpen(false);
      setError(null);
    } catch (err) {
      setError('Failed to create restock request: ' + (err.response?.data?.detail || err.message));
      console.error('Restock error:', err);
    }
  };

  const handleAddInventory = () => {
    setAddFormData({
      item_id: '',
      area_id: '',
      quantity: 0,
      threshold: 0,
      safety_stock: 0,
    });
    setAddDialogOpen(true);
  };

  const handleSaveAddInventory = async () => {
    try {
      if (!addFormData.item_id || !addFormData.area_id) {
        setError('Please select both item and area');
        return;
      }
      
      if (addFormData.quantity < 0 || addFormData.threshold < 0 || addFormData.safety_stock < 0) {
        setError('Quantities cannot be negative');
        return;
      }
      
      // Check if this item/area combination already exists
      const existingInventory = inventory.find(inv => 
        inv.item_id === addFormData.item_id && inv.area_id === addFormData.area_id
      );
      
      if (existingInventory) {
        setError('This item already exists in the selected area. Please choose a different item or area.');
        return;
      }
      
      await inventoryAPI.create(addFormData);
      setAddDialogOpen(false);
      setError(null);
      fetchInventory();
      fetchAreas(); // Refresh areas in case new area was added
    } catch (err) {
      setError('Failed to add inventory item: ' + (err.response?.data?.detail || err.message));
      console.error('Add inventory error:', err);
    }
  };

  const getStockStatus = (quantity, threshold) => {
    if (quantity <= 0) return { label: 'Out of Stock', color: 'error' };
    if (quantity < threshold) return { label: 'Low Stock', color: 'warning' };
    return { label: 'In Stock', color: 'success' };
  };

  const columns = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'item_id', headerName: 'Item ID', width: 100 },
    { field: 'area_id', headerName: 'Area ID', width: 100 },
    {
      field: 'quantity',
      headerName: 'Quantity',
      width: 120,
      renderCell: (params) => (
        <Box display="flex" alignItems="center">
          {params.value}
          {params.value < params.row.threshold && (
            <WarningIcon color="warning" sx={{ ml: 1, fontSize: 16 }} />
          )}
        </Box>
      ),
    },
    { field: 'threshold', headerName: 'Threshold', width: 120 },
    { field: 'safety_stock', headerName: 'Safety Stock', width: 120 },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      renderCell: (params) => {
        const status = getStockStatus(params.row.quantity, params.row.threshold);
        return <Chip label={status.label} color={status.color} size="small" />;
      },
    },
    {
      field: 'last_updated',
      headerName: 'Last Updated',
      width: 150,
      renderCell: (params) => new Date(params.value).toLocaleDateString(),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 150,
      renderCell: (params) => (
        <Box>
          <IconButton
            size="small"
            onClick={() => handleEditClick(params.row)}
            title="Edit"
          >
            <EditIcon />
          </IconButton>
          <IconButton
            size="small"
            onClick={() => handleRequestRestock(params.row)}
            title="Request Restock"
            color="primary"
          >
            <InventoryIcon />
          </IconButton>
        </Box>
      ),
    },
  ];

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Inventory Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddInventory}
        >
          Add Inventory Item
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={inventory}
          columns={columns}
          pageSize={10}
          rowsPerPageOptions={[10, 25, 50]}
          disableSelectionOnClick
          sx={{
            '& .MuiDataGrid-cell': {
              borderBottom: '1px solid #e0e0e0',
            },
          }}
        />
      </Paper>

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Inventory Item</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Quantity"
                type="number"
                value={formData.quantity}
                onChange={(e) => setFormData({ ...formData, quantity: parseInt(e.target.value) || 0 })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Threshold"
                type="number"
                value={formData.threshold}
                onChange={(e) => setFormData({ ...formData, threshold: parseInt(e.target.value) || 0 })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Safety Stock"
                type="number"
                value={formData.safety_stock}
                onChange={(e) => setFormData({ ...formData, safety_stock: parseInt(e.target.value) || 0 })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSave} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>

      {/* Request Restock Dialog */}
      <Dialog open={restockDialogOpen} onClose={() => setRestockDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Request Restock</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <Typography variant="body2" color="text.secondary">
                Item ID: {selectedItem?.item_id} | Area ID: {selectedItem?.area_id}
              </Typography>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="body2" color="text.secondary">
                Current Stock: {selectedItem?.quantity} | Threshold: {selectedItem?.threshold}
              </Typography>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Quantity to Request"
                type="number"
                value={restockForm.quantity_requested}
                onChange={(e) => setRestockForm({ ...restockForm, quantity_requested: parseInt(e.target.value) || 0 })}
                helperText="Enter the quantity you want to restock"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRestockDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveRestock} variant="contained">Request Restock</Button>
        </DialogActions>
      </Dialog>

      {/* Add Inventory Dialog */}
      <Dialog open={addDialogOpen} onClose={() => setAddDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Inventory Item</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                select
                label="Item"
                value={addFormData.item_id}
                onChange={(e) => setAddFormData({ ...addFormData, item_id: parseInt(e.target.value) })}
                SelectProps={{ native: true }}
              >
                <option value="">Select Item</option>
                {items.map(item => (
                  <option key={item.id} value={item.id}>{item.name} ({item.sku})</option>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                select
                label="Area"
                value={addFormData.area_id}
                onChange={(e) => setAddFormData({ ...addFormData, area_id: parseInt(e.target.value) })}
                SelectProps={{ native: true }}
              >
                <option value="">Select Area</option>
                {areas.map(area => (
                  <option key={area.id} value={area.id}>{area.name}</option>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Quantity"
                type="number"
                value={addFormData.quantity}
                onChange={(e) => setAddFormData({ ...addFormData, quantity: parseInt(e.target.value) || 0 })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Threshold"
                type="number"
                value={addFormData.threshold}
                onChange={(e) => setAddFormData({ ...addFormData, threshold: parseInt(e.target.value) || 0 })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Safety Stock"
                type="number"
                value={addFormData.safety_stock}
                onChange={(e) => setAddFormData({ ...addFormData, safety_stock: parseInt(e.target.value) || 0 })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveAddInventory} variant="contained">Add Inventory Item</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Inventory;
