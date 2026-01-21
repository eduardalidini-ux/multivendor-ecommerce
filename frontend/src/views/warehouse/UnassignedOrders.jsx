import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import useAxios from '../../utils/useAxios'

function UnassignedOrders() {
    const axios = useAxios()
    const [orders, setOrders] = useState([])
    const [loading, setLoading] = useState(true)

    const fetchOrders = async () => {
        setLoading(true)
        try {
            const res = await axios.get('warehouse/orders/unassigned/')
            setOrders(res.data)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchOrders()
    }, [])

    return (
        <div className='container mt-5' style={{ marginBottom: 150 }}>
            <div className='d-flex align-items-center justify-content-between mb-3'>
                <h3 className='mb-0'>Unassigned Orders</h3>
                <div>
                    <Link className='btn btn-outline-secondary me-2' to='/warehouse/dashboard'>Dashboard</Link>
                    <button className='btn btn-primary' onClick={fetchOrders} disabled={loading}>Refresh</button>
                </div>
            </div>

            <div className='rounded shadow p-3 bg-white'>
                {loading ? (
                    <div className='text-center'>Loading...</div>
                ) : (
                    <table className='table align-middle mb-0 bg-white'>
                        <thead className='bg-light'>
                            <tr>
                                <th>Order ID</th>
                                <th>Customer</th>
                                <th>Payment</th>
                                <th>Order Status</th>
                                <th>Shipping Address</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {(orders || []).map((o) => (
                                <tr key={o.id}>
                                    <td>#{o.oid}</td>
                                    <td>
                                        <div className='fw-bold'>{o.full_name}</div>
                                        <div className='text-muted'>{o.email}</div>
                                    </td>
                                    <td>{String(o.payment_status || '').toUpperCase()}</td>
                                    <td>{o.order_status}</td>
                                    <td>
                                        <div>{o.address}</div>
                                        <div className='text-muted'>{[o.city, o.state, o.country].filter(Boolean).join(', ')}</div>
                                    </td>
                                    <td>
                                        <Link className='btn btn-sm btn-primary' to={`/warehouse/orders/${o.oid}`}>Assign</Link>
                                    </td>
                                </tr>
                            ))}
                            {(!orders || orders.length === 0) && (
                                <tr>
                                    <td colSpan={6} className='text-center'>No unassigned orders.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    )
}

export default UnassignedOrders
