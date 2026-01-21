import React, { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import useAxios from '../../utils/useAxios'

function Shipments() {
    const axios = useAxios()

    const [shipments, setShipments] = useState([])
    const [loading, setLoading] = useState(true)
    const [statusFilter, setStatusFilter] = useState('')

    const fetchShipments = async (status) => {
        setLoading(true)
        try {
            const qs = status ? `?status=${encodeURIComponent(status)}` : ''
            const res = await axios.get(`warehouse/shipments/${qs}`)
            setShipments(res.data || [])
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchShipments(statusFilter)
    }, [statusFilter])

    const counts = useMemo(() => {
        const c = {
            total: shipments.length,
            pending_assignment: 0,
            assigned: 0,
            picked_up: 0,
            out_for_delivery: 0,
            delivered: 0,
            failed: 0,
            returned: 0,
        }
        for (const s of shipments) {
            if (s?.status && c[s.status] !== undefined) c[s.status] += 1
        }
        return c
    }, [shipments])

    return (
        <div className='container mt-5' style={{ marginBottom: 150 }}>
            <div className='d-flex align-items-center justify-content-between mb-3'>
                <h3 className='mb-0'>All Shipments</h3>
                <div>
                    <Link className='btn btn-outline-secondary me-2' to='/warehouse/dashboard'>Dashboard</Link>
                    <Link className='btn btn-outline-secondary me-2' to='/warehouse/orders'>Unassigned Orders</Link>
                    <button className='btn btn-primary' onClick={() => fetchShipments(statusFilter)} disabled={loading}>Refresh</button>
                </div>
            </div>

            <div className='row gx-xl-5 mb-4'>
                <div className='col-lg-3 mb-3'>
                    <div className='rounded shadow' style={{ backgroundColor: '#BBDEFB' }}>
                        <div className='card-body'>
                            <p className='mb-1'>Total</p>
                            <h2 className='mb-0'>{counts.total}</h2>
                        </div>
                    </div>
                </div>
                <div className='col-lg-9 mb-3'>
                    <label className='form-label'>Filter by status</label>
                    <select className='form-select' value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                        <option value=''>All</option>
                        <option value='pending_assignment'>Pending Assignment</option>
                        <option value='assigned'>Assigned</option>
                        <option value='picked_up'>Picked Up</option>
                        <option value='out_for_delivery'>Out For Delivery</option>
                        <option value='delivered'>Delivered</option>
                        <option value='failed'>Failed</option>
                        <option value='returned'>Returned</option>
                    </select>
                </div>
            </div>

            <div className='rounded shadow p-3 bg-white'>
                {loading ? (
                    <div className='text-center'>Loading...</div>
                ) : (
                    <table className='table align-middle mb-0 bg-white'>
                        <thead className='bg-light'>
                            <tr>
                                <th>Shipment</th>
                                <th>Order</th>
                                <th>Courier</th>
                                <th>Status</th>
                                <th>Last Update</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {(shipments || []).map((s) => (
                                <tr key={s.id}>
                                    <td>#{s.id}</td>
                                    <td>
                                        <div className='fw-bold'>#{s.order?.oid}</div>
                                        <div className='text-muted' style={{ fontSize: 12 }}>{s.order?.full_name}</div>
                                    </td>
                                    <td>{s.courier?.full_name || s.courier?.email || '—'}</td>
                                    <td>{s.status}</td>
                                    <td className='text-muted' style={{ fontSize: 12 }}>{s.updated_at ? new Date(s.updated_at).toLocaleString() : '—'}</td>
                                    <td>
                                        {s.order?.oid && (
                                            <Link className='btn btn-sm btn-outline-primary' to={`/track/order/${s.order.oid}`}>Open Tracking</Link>
                                        )}
                                    </td>
                                </tr>
                            ))}
                            {(!shipments || shipments.length === 0) && (
                                <tr>
                                    <td colSpan={6} className='text-center'>No shipments found.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    )
}

export default Shipments
