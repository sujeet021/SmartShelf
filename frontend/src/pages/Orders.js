import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Chip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
} from '@mui/material';
import {
  Add as AddIcon,
} from '@mui/icons-material';
import { DataGrid } from '@mui/x-data-grid';
import { ordersAPI, itemsAPI, inventoryAPI } from '../services/api';

function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [items, setItems] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [orderForm, setOrderForm] = useState({
    order_reference: '',
    area_id: '',
    order_lines: [{ item_id: '', quantity: 1, price: 0 }]
  });

  useEffect(() => {
    fetchOrders();
    fetchItems();
    fetchInventory();
  }, []);

  const fetchItems = async () => {
    try {
      const response = await itemsAPI.getAll();
      setItems(response.data || []);
    } catch (err) {
      console.error('Items error:', err);
    }
  };

  const fetchInventory = async () => {
    try {
      const response = await inventoryAPI.getAll();
      setInventory(response.data || []);
    } catch (err) {
      console.error('Inventory error:', err);
    }
  };

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const response = await ordersAPI.getAll();
      setOrders(response.data || []);
    } catch (err) {
      setError('Failed to fetch orders data');
      console.error('Orders error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateOrder = () => {
    setOrderForm({
      order_reference: `ORD-${new Date().getFullYear()}-${String(orders.length + 1).padStart(3, '0')}`,
      area_id: '',
      order_lines: [{ item_id: '', quantity: 1, price: 0 }]
    });
    setCreateDialogOpen(true);
  };

  const handleAddOrderLine = () => {
    setOrderForm({
      ...orderForm,
      order_lines: [...orderForm.order_lines, { item_id: '', quantity: 1, price: 0 }]
    });
  };

  const handleRemoveOrderLine = (index) => {
    if (orderForm.order_lines.length > 1) {
      setOrderForm({
        ...orderForm,
        order_lines: orderForm.order_lines.filter((_, i) => i !== index)
      });
    }
  };

  const handleOrderLineChange = (index, field, value) => {
    const newOrderLines = [...orderForm.order_lines];
    newOrderLines[index][field] = field === 'quantity' || field === 'price' ? parseFloat(value) || 0 : value;
    setOrderForm({ ...orderForm, order_lines: newOrderLines });
  };

  const handleSaveOrder = async () => {
    try {
      // Basic validation
      if (!orderForm.order_reference || !orderForm.area_id) {
        setError('Please fill in all required fields');
        return;
      }
      
      if (orderForm.order_lines.length === 0 || orderForm.order_lines.some(line => !line.item_id || !line.quantity)) {
        setError('Please add at least one item with quantity');
        return;
      }
      
      await ordersAPI.create(orderForm);
      setCreateDialogOpen(false);
      setError(null);
      fetchOrders();
    } catch (err) {
      setError('Failed to create order: ' + (err.response?.data?.detail || err.message));
      console.error('Create order error:', err);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'placed': return 'warning';
      case 'fulfilled': return 'success';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  const getAvailableAreas = () => {
    const uniqueAreas = [...new Set(inventory.map(inv => inv.area_id))];
    return uniqueAreas;
  };

  const columns = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'order_reference', headerName: 'Order Ref', width: 150 },
    { field: 'area_id', headerName: 'Area ID', width: 100 },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value}
          color={getStatusColor(params.value)}
          size="small"
        />
      ),
    },
    {
      field: 'created_at',
      headerName: 'Created',
      width: 150,
      renderCell: (params) => new Date(params.value).toLocaleDateString(),
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
          Orders Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateOrder}
        >
          Create Order
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={orders}
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

      {/* Create Order Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Order</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Order Reference"
                value={orderForm.order_reference}
                onChange={(e) => setOrderForm({ ...orderForm, order_reference: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Area"
                value={orderForm.area_id}
                onChange={(e) => setOrderForm({ ...orderForm, area_id: parseInt(e.target.value) })}
                SelectProps={{ native: true }}
              >
                <option value="">Select Area</option>
                {getAvailableAreas().map(areaId => (
                  <option key={areaId} value={areaId}>Area {areaId}</option>
                ))}
              </TextField>
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>Order Items</Typography>
              {orderForm.order_lines.map((line, index) => (
                <Grid container spacing={2} key={index} sx={{ mb: 2, p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      fullWidth
                      select
                      label="Item"
                      value={line.item_id}
                      onChange={(e) => handleOrderLineChange(index, 'item_id', parseInt(e.target.value))}
                      SelectProps={{ native: true }}
                    >
                      <option value="">Select Item</option>
                      {items.map(item => (
                        <option key={item.id} value={item.id}>{item.name} ({item.sku})</option>
                      ))}
                    </TextField>
                  </Grid>
                  <Grid item xs={12} sm={3}>
                    <TextField
                      fullWidth
                      label="Quantity"
                      type="number"
                      value={line.quantity}
                      onChange={(e) => handleOrderLineChange(index, 'quantity', e.target.value)}
                    />
                  </Grid>
                  <Grid item xs={12} sm={3}>
                    <TextField
                      fullWidth
                      label="Price"
                      type="number"
                      value={line.price}
                      onChange={(e) => handleOrderLineChange(index, 'price', e.target.value)}
                    />
                  </Grid>
                  <Grid item xs={12} sm={2}>
                    <Button
                      variant="outlined"
                      color="error"
                      onClick={() => handleRemoveOrderLine(index)}
                      disabled={orderForm.order_lines.length === 1}
                    >
                      Remove
                    </Button>
                  </Grid>
                </Grid>
              ))}
              <Button
                variant="outlined"
                onClick={handleAddOrderLine}
                sx={{ mt: 1 }}
              >
                Add Item
              </Button>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveOrder} variant="contained">Create Order</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Orders;
