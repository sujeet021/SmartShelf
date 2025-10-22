import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Chip,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Inventory as InventoryIcon,
  Warning as WarningIcon,
  ShoppingCart as ShoppingCartIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';
import { inventoryAPI, alertsAPI, ordersAPI } from '../services/api';

function Dashboard() {
  const [stats, setStats] = useState({
    totalItems: 0,
    lowStockItems: 0,
    totalOrders: 0,
    pendingAlerts: 0,
  });
  const [recentAlerts, setRecentAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [inventoryRes, alertsRes, ordersRes] = await Promise.all([
        inventoryAPI.getAll().catch(() => ({ data: [] })),
        alertsAPI.getUnresolved().catch(() => ({ data: [] })),
        ordersAPI.getAll().catch(() => ({ data: [] })),
      ]);

      const inventory = inventoryRes.data || [];
      const alerts = alertsRes.data || [];
      const orders = ordersRes.data || [];

      setStats({
        totalItems: inventory.length,
        lowStockItems: inventory.filter(item => item.quantity < item.threshold).length,
        totalOrders: orders.length,
        pendingAlerts: alerts.length,
      });

      setRecentAlerts(alerts.slice(0, 5));
    } catch (err) {
      setError('Failed to fetch dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, icon, color = 'primary' }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="h6">
              {title}
            </Typography>
            <Typography variant="h4" component="h2">
              {value}
            </Typography>
          </Box>
          <Box
            sx={{
              backgroundColor: `${color}.light`,
              borderRadius: '50%',
              p: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Statistics Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Items"
            value={stats.totalItems}
            icon={<InventoryIcon />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Low Stock Items"
            value={stats.lowStockItems}
            icon={<WarningIcon />}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Orders"
            value={stats.totalOrders}
            icon={<ShoppingCartIcon />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Pending Alerts"
            value={stats.pendingAlerts}
            icon={<TrendingUpIcon />}
            color="error"
          />
        </Grid>

        {/* Recent Alerts */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Alerts
            </Typography>
            {recentAlerts.length > 0 ? (
              <List>
                {recentAlerts.map((alert) => (
                  <ListItem key={alert.id} divider>
                    <ListItemText
                      primary={alert.type}
                      secondary={`Item ID: ${alert.item_id} - Area ID: ${alert.area_id}`}
                    />
                    <Chip
                      label={alert.resolved ? 'Resolved' : 'Pending'}
                      color={alert.resolved ? 'success' : 'warning'}
                      size="small"
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography color="textSecondary">
                No recent alerts
              </Typography>
            )}
          </Paper>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <List>
              <ListItem>
                <ListItemText
                  primary="View Low Stock Items"
                  secondary="Check items that need restocking"
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Create New Order"
                  secondary="Add a new order to the system"
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Manage Inventory"
                  secondary="Update stock levels and thresholds"
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard;
