import React, { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import useAxios from '../../utils/useAxios'

function Dashboard() {
    const axios = useAxios()
    const [orders, setOrders] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        axios.get('warehouse/orders/unassigned/').then((res) => {
            setOrders(res.data)
            setLoading(false)
        }).catch(() => {
            setLoading(false)
        })
    }, [])

    const counts = useMemo(() => {
        return {
            unassigned: orders?.length || 0,
        }
    }, [orders])

    return (
        <div className='container mt-5' style={{ marginBottom: 150 }}>
            <div className='row'>
                <div className='col-lg-12'>
                    <div className='d-flex align-items-center justify-content-between'>
                        <h3 className='mb-3'>Warehouse Dashboard</h3>
                        <Link className='btn btn-outline-secondary' to='/'>Home</Link>
                    </div>

                    <div className='row gx-xl-5 mb-4'>
                        <div className='col-lg-4 mb-3'>
                            <div className='rounded shadow' style={{ backgroundColor: '#B2DFDB' }}>
                                <div className='card-body'>
                                    <p className='mb-1'>Unassigned Orders</p>
                                    <h2 className='mb-0'>{counts.unassigned}</h2>
                                </div>
                            </div>
                        </div>
                        <div className='col-lg-8 mb-3 d-flex align-items-end justify-content-end'>
                            <Link className='btn btn-primary' to='/warehouse/orders'>Go to Unassigned Orders</Link>
                        </div>
                    </div>

                    {loading && (
                        <div className='text-center'>Loading...</div>
                    )}

                    {!loading && (
                        <div className='rounded shadow p-3 bg-white'>
                            <div className='d-flex align-items-center justify-content-between mb-3'>
                                <h5 className='mb-0'>Recently Unassigned Orders</h5>
                                <Link className='btn btn-sm btn-outline-primary' to='/warehouse/orders'>View all</Link>
                            </div>
                            <table className='table align-middle mb-0 bg-white'>
                                <thead className='bg-light'>
                                    <tr>
                                        <th>Order ID</th>
                                        <th>Customer</th>
                                        <th>Payment Status</th>
                                        <th>Order Status</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {(orders || []).slice(0, 8).map((o) => (
                                        <tr key={o.id}>
                                            <td>#{o.oid}</td>
                                            <td>{o.full_name}</td>
                                            <td>{String(o.payment_status || '').toUpperCase()}</td>
                                            <td>{o.order_status}</td>
                                            <td>
                                                <Link className='btn btn-sm btn-primary' to={`/warehouse/orders/${o.oid}`}>Assign</Link>
                                            </td>
                                        </tr>
                                    ))}
                                    {(!orders || orders.length === 0) && (
                                        <tr>
                                            <td colSpan={5} className='text-center'>No unassigned orders.</td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

export default Dashboard
