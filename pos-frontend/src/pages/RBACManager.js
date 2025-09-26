import React, { useState, useEffect } from 'react';
import api from '../api';
import './RBACManager.css';

const RBACManager = () => {
  const [activeTab, setActiveTab] = useState('roles');
  const [roles, setRoles] = useState([]);
  const [permissions, setPermissions] = useState([]);
  const [users, setUsers] = useState([]);
  const [selectedRole, setSelectedRole] = useState(null);
  const [selectedUser, setSelectedUser] = useState(null);
  const [rolePermissions, setRolePermissions] = useState([]);
  const [userPermissions, setUserPermissions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load roles summary
      const rolesResponse = await api.get('/rbac/roles/summary');
      setRoles(rolesResponse.data);

      // Load all permissions
      const permissionsResponse = await api.get('/rbac/permissions');
      setPermissions(permissionsResponse.data);

      // Load users
      const usersResponse = await api.get('/auth/users');
      setUsers(usersResponse.data);
    } catch (error) {
      console.error('Error loading RBAC data:', error);
      setMessage('Error loading data');
    } finally {
      setLoading(false);
    }
  };

  const handleRoleSelect = async (role) => {
    setSelectedRole(role);
    try {
      const response = await api.get(`/rbac/roles/${role}/permissions`);
      setRolePermissions(response.data);
    } catch (error) {
      console.error('Error loading role permissions:', error);
    }
  };

  const handleUserSelect = async (user) => {
    setSelectedUser(user);
    try {
      const response = await api.get(`/rbac/users/${user.id}/permissions`);
      setUserPermissions(response.data.permissions);
    } catch (error) {
      console.error('Error loading user permissions:', error);
    }
  };

  const handleRolePermissionUpdate = async (permissionIds) => {
    if (!selectedRole) return;
    
    try {
      await api.post(`/rbac/roles/${selectedRole}/permissions`, {
        role: selectedRole,
        permissions: permissionIds
      });
      setMessage('Role permissions updated successfully');
      handleRoleSelect(selectedRole);
    } catch (error) {
      console.error('Error updating role permissions:', error);
      setMessage('Error updating role permissions');
    }
  };

  const handleUserPermissionUpdate = async (permissionIds, isGranted = true) => {
    if (!selectedUser) return;
    
    try {
      await api.post(`/rbac/users/${selectedUser.id}/permissions`, {
        user_id: selectedUser.id,
        permissions: permissionIds,
        is_granted: isGranted
      });
      setMessage('User permissions updated successfully');
      handleUserSelect(selectedUser);
    } catch (error) {
      console.error('Error updating user permissions:', error);
      setMessage('Error updating user permissions');
    }
  };

  const handleUserRoleUpdate = async (userId, newRole) => {
    try {
      await api.put(`/rbac/users/${userId}/role`, {
        role: newRole
      });
      setMessage('User role updated successfully');
      loadData();
    } catch (error) {
      console.error('Error updating user role:', error);
      setMessage('Error updating user role');
    }
  };

  const initializeRBAC = async () => {
    try {
      await api.post('/rbac/initialize');
      setMessage('RBAC system initialized successfully');
      loadData();
    } catch (error) {
      console.error('Error initializing RBAC:', error);
      setMessage('Error initializing RBAC system');
    }
  };

  const PermissionSelector = ({ permissions, selectedPermissions, onUpdate, title }) => {
    const [selected, setSelected] = useState(selectedPermissions || []);

    const handlePermissionToggle = (permissionId) => {
      const newSelected = selected.includes(permissionId)
        ? selected.filter(id => id !== permissionId)
        : [...selected, permissionId];
      setSelected(newSelected);
    };

    const handleSave = () => {
      onUpdate(selected);
    };

    const groupedPermissions = permissions.reduce((groups, permission) => {
      const resource = permission.resource;
      if (!groups[resource]) {
        groups[resource] = [];
      }
      groups[resource].push(permission);
      return groups;
    }, {});

    return (
      <div className="permission-selector">
        <h3>{title}</h3>
        <div className="permission-groups">
          {Object.entries(groupedPermissions).map(([resource, perms]) => (
            <div key={resource} className="permission-group">
              <h4>{resource.charAt(0).toUpperCase() + resource.slice(1)}</h4>
              <div className="permission-list">
                {perms.map(permission => (
                  <label key={permission.id} className="permission-item">
                    <input
                      type="checkbox"
                      checked={selected.includes(permission.id)}
                      onChange={() => handlePermissionToggle(permission.id)}
                    />
                    <span>{permission.description || permission.name}</span>
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>
        <button onClick={handleSave} className="save-btn">
          Save Permissions
        </button>
      </div>
    );
  };

  if (loading) {
    return <div className="loading">Loading RBAC Manager...</div>;
  }

  return (
    <div className="rbac-manager">
      <div className="rbac-header">
        <h2>🔐 Role-Based Access Control</h2>
        <button onClick={initializeRBAC} className="init-btn">
          Initialize RBAC System
        </button>
      </div>

      {message && (
        <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}

      <div className="rbac-tabs">
        <button
          className={`tab ${activeTab === 'roles' ? 'active' : ''}`}
          onClick={() => setActiveTab('roles')}
        >
          👥 Role Management
        </button>
        <button
          className={`tab ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          👤 User Management
        </button>
        <button
          className={`tab ${activeTab === 'permissions' ? 'active' : ''}`}
          onClick={() => setActiveTab('permissions')}
        >
          🔑 Permissions
        </button>
      </div>

      <div className="rbac-content">
        {activeTab === 'roles' && (
          <div className="roles-section">
            <div className="roles-list">
              <h3>Available Roles</h3>
              <div className="role-cards">
                {roles.map(role => (
                  <div
                    key={role.role}
                    className={`role-card ${selectedRole === role.role ? 'selected' : ''}`}
                    onClick={() => handleRoleSelect(role.role)}
                  >
                    <h4>{role.role}</h4>
                    <p>Users: {role.total_users}</p>
                    <p>Permissions: {role.total_permissions}</p>
                    <p>Status: {role.is_active ? 'Active' : 'Inactive'}</p>
                  </div>
                ))}
              </div>
            </div>

            {selectedRole && (
              <div className="role-permissions">
                <h3>Permissions for {selectedRole}</h3>
                <PermissionSelector
                  permissions={permissions}
                  selectedPermissions={rolePermissions.map(p => p.id)}
                  onUpdate={handleRolePermissionUpdate}
                  title={`Edit Permissions for ${selectedRole}`}
                />
              </div>
            )}
          </div>
        )}

        {activeTab === 'users' && (
          <div className="users-section">
            <div className="users-list">
              <h3>Users</h3>
              <div className="user-cards">
                {users.map(user => (
                  <div
                    key={user.id}
                    className={`user-card ${selectedUser?.id === user.id ? 'selected' : ''}`}
                    onClick={() => handleUserSelect(user)}
                  >
                    <h4>{user.username}</h4>
                    <p>Email: {user.email}</p>
                    <p>Role: {user.role}</p>
                    <p>Status: {user.is_active ? 'Active' : 'Inactive'}</p>
                  </div>
                ))}
              </div>
            </div>

            {selectedUser && (
              <div className="user-permissions">
                <h3>User: {selectedUser.username}</h3>
                <div className="user-role-update">
                  <h4>Update Role</h4>
                  <select
                    value={selectedUser.role}
                    onChange={(e) => handleUserRoleUpdate(selectedUser.id, e.target.value)}
                  >
                    <option value="admin">Admin</option>
                    <option value="cashier">Cashier</option>
                    <option value="inventory_manager">Inventory Manager</option>
                    <option value="manager">Manager</option>
                    <option value="viewer">Viewer</option>
                  </select>
                </div>
                <PermissionSelector
                  permissions={permissions}
                  selectedPermissions={userPermissions}
                  onUpdate={(permissionIds) => handleUserPermissionUpdate(permissionIds, true)}
                  title="Individual User Permissions"
                />
              </div>
            )}
          </div>
        )}

        {activeTab === 'permissions' && (
          <div className="permissions-section">
            <h3>All Available Permissions</h3>
            <div className="permissions-list">
              {permissions.map(permission => (
                <div key={permission.id} className="permission-item">
                  <h4>{permission.name}</h4>
                  <p>{permission.description}</p>
                  <p>Resource: {permission.resource}</p>
                  <p>Action: {permission.action}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RBACManager; 