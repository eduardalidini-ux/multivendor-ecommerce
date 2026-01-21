import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import useAxios from '../../utils/useAxios'

function Dashboard() {
    const axios = useAxios()
    const [shipments, setShipments] = useState([])
    const [loading, setLoading] = useState(true)

    const fetchShipments = async () => {
        setLoading(true)
        try {
            const res = await axios.get('warehouse/courier/my-shipments/')
            setShipments(res.data || [])
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchShipments()
    }, [])

    return (
        <div className='container mt-5' style={{ marginBottom: 150 }}>
            <div className='d-flex align-items-center justify-content-between mb-3'>
                <h3 className='mb-0'>Courier Dashboard</h3>
                <div>
                    <button className='btn btn-primary' onClick={fetchShipments} disabled={loading}>Refresh</button>
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
                                <th>Status</th>
                                <th>Destination</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {(shipments || []).map((s) => (
                                <tr key={s.id}>
                                    <td>#{s.id}</td>
                                    <td>#{s.order?.oid}</td>
                                    <td>{s.status}</td>
                                    <td>
                                        <div>{s.order?.address}</div>
                                        <div className='text-muted'>{[s.order?.city, s.order?.state, s.order?.country].filter(Boolean).join(', ')}</div>
                                    </td>
                                    <td>
                                        <Link className='btn btn-sm btn-primary' to={`/courier/shipments/${s.id}`}>Open</Link>
                                        {s.order?.oid && (
                                            <Link className='btn btn-sm btn-outline-secondary ms-2' to={`/track/order/${s.order.oid}`}>Tracking</Link>
                                        )}
                                    </td>
                                </tr>
                            ))}
                            {(!shipments || shipments.length === 0) && (
                                <tr>
                                    <td colSpan={5} className='text-center'>No assigned shipments.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    )
}

export default Dashboard
